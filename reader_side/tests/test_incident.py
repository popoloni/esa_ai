"""Adversarial CP12 checks use real CP11 SQLite files and fresh worker processes."""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from incident_core import (CONFIG, REVIEW, HISTORY, REFERENCE_HISTORY, REFERENCE_CONFIG,
    REFERENCE_REVIEW, SUCCESS, REPRODUCED, evaluate_incident, rehearse_incident,
    service_event, new_workspace, tree_hashes, read_json, write_json, environment)
from scope_guard import capture_edit_scope


@contextmanager
def replaced(path, content):
    original = path.read_bytes()
    path.write_bytes(content if isinstance(content, bytes) else content.encode())
    try:
        yield
    finally:
        path.write_bytes(original)


class IncidentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="cp12-focused-")
        cls.directory = Path(cls.temporary.name)
        cls.root = cls.directory / "companion"
        shutil.copytree(TOOLS.parents[1], cls.root,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "evidence"))
        cls.session = cls.directory / "reference_session"
        cls.record = rehearse_incident(cls.session, cls.root, reference=True)
        cls.reference_output = cls.directory / "reference_review"
        cls.good = evaluate_incident(cls.session, cls.root, reference=True, output=cls.reference_output)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.case = self.directory / self._testMethodName
        self.case.mkdir()

    def event(self, name):
        return read_json(self.session / "steps" / (name + ".json"))

    def gate(self, **kwargs):
        return evaluate_incident(self.session, self.root, output=self.case / "review", **kwargs)

    def config(self, value):
        return replaced(self.root / CONFIG, json.dumps(value))

    def service(self, workspace, config=None):
        return service_event(workspace, config or self.root / CONFIG,
                             self.root / REFERENCE_HISTORY, "inspect", {}, "NEGATIVE_PROBE", self.root)

    def test_reference_reproduces_fault_and_validates_recovery(self):
        self.assertEqual(self.record["status"], REPRODUCED, self.record["findings"])
        self.assertEqual(self.good["status"], SUCCESS, self.good["findings"])
        self.assertTrue(all(check["passed"] for check in self.good["checks"]))
        self.assertTrue(self.good["rehearsal_originals_unchanged"])

    def test_path_only_control_changes_exactly_one_configuration_field(self):
        control, fault = self.event("S04_control_current"), self.event("S06_fault_current")
        changed = {key for key in control["config"] if control["config"][key] != fault["config"][key]}
        self.assertEqual(changed, {"state_path"})
        self.assertEqual(control["arguments"], fault["arguments"])
        self.assertEqual(control["source_sha256"], fault["source_sha256"])
        self.assertNotEqual(control["result"]["record"]["decision"], fault["result"]["record"]["decision"])

    def test_equal_historical_decision_id_does_not_prove_replay(self):
        control, fault = self.event("S05_control_history"), self.event("S07_fault_history")
        self.assertEqual(control["result"]["record"]["decision_id"], fault["result"]["record"]["decision_id"])
        self.assertEqual(control["result"]["status"], "REPLAYED")
        self.assertEqual(fault["result"]["status"], "CREATED")
        self.assertNotEqual(control["database_path"], fault["database_path"])
        self.assertEqual(fault["state_after"]["audit_count"], fault["state_before"]["audit_count"] + 1)

    def test_retry_is_idempotent_within_the_wrong_ledger(self):
        event = self.event("S08_incident_retry")
        self.assertEqual(event["result"]["status"], "REPLAYED")
        self.assertEqual(event["state_before"], event["state_after"])

    def test_explicit_v2_probe_rules_out_threshold_implementation_regression(self):
        event = self.event("S09_explicit_v2")
        self.assertEqual(event["state_after"]["active_policy"], "BR-001/v1")
        self.assertEqual(event["result"]["record"]["decision"]["route"], "HUMAN_REVIEW")
        self.assertEqual(event["result"]["record"]["policy_version"], "BR-001/v2")

    def test_recovery_does_not_claim_reconciliation_or_production_authority(self):
        self.assertEqual(self.good["restoration_status"], "VALIDATED_LOCAL_SELECTION")
        self.assertEqual(self.good["reconciliation_status"], "QUARANTINED_PENDING_OWNER_RECONCILIATION")
        self.assertEqual(self.good["permanent_fix_status"], "LOCAL_GUARD_VALIDATED_NO_PRODUCTION_ROLLOUT")
        self.assertEqual(self.good["authority"]["CP07_T07_04"], "BLOCKED")
        for key in ("real_release_authorized", "production_recovery_authorized", "incident_closed", "payment_authorized"):
            self.assertIs(self.good["authority"][key], False)

    def test_protected_unsafe_fixture_remains_failing_after_current_repair(self):
        with replaced(self.root / CONFIG, (self.root / REFERENCE_CONFIG).read_bytes()), \
             replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()):
            result = self.gate(unsafe=True)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("DEPLOYMENT:state_path", result["findings"])
        self.assertIn("INCIDENT_REVIEW:root_cause", result["findings"])
        self.assertTrue(any(name.startswith("RECOVERY:") for name in result["findings"]))

    def test_current_repair_passes_actual_cp12_edit_scope(self):
        with replaced(self.root / HISTORY, (self.root / REFERENCE_HISTORY).read_bytes()):
            session = self.case / "current_session"
            self.assertEqual(rehearse_incident(session, self.root)["status"], REPRODUCED)
            baseline = self.case / "baseline.json"
            write_json(baseline, capture_edit_scope("CP12", self.root))
            with replaced(self.root / CONFIG, (self.root / REFERENCE_CONFIG).read_bytes()), \
                 replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()):
                result = evaluate_incident(session, self.root, output=self.case / "current_review", scope_baseline=baseline)
            self.assertEqual(result["status"], SUCCESS, result["findings"])
            self.assertEqual(result["mode"], "WORKING_CANDIDATES")
            self.assertTrue(result["edit_scope_checked"])

    def test_guards_reject_before_initializing_missing_state(self):
        workspace = new_workspace(self.case / "workspace", self.root)
        result = self.service(workspace, self.root / REFERENCE_CONFIG)
        self.assertEqual(result["error"], "STATE_MISSING_INITIALIZATION_FORBIDDEN")
        self.assertFalse(list(workspace.rglob("*.sqlite")))

    def test_binding_on_missing_state_cannot_authorize_initialization(self):
        config = read_json(self.root / REFERENCE_CONFIG)
        config["initialize_missing_state"] = True
        workspace = new_workspace(self.case / "workspace", self.root)
        with self.config(config):
            result = self.service(workspace)
        self.assertEqual(result["error"], "STATE_BINDING_UNAVAILABLE")
        self.assertFalse(list(workspace.rglob("*.sqlite")))

    def test_recovery_rejects_wrong_active_policy_and_missing_anchor(self):
        wrong = read_json(self.reference_output / "steps/G02_wrong_active_policy.json")
        anchor = read_json(self.reference_output / "steps/G03_missing_anchor.json")
        self.assertEqual(wrong["error"], "ACTIVE_POLICY_BINDING_MISMATCH")
        self.assertEqual(anchor["error"], "HISTORICAL_ANCHOR_MISSING")
        self.assertEqual(wrong["state_before"], wrong["state_after"])
        self.assertEqual(anchor["state_before"], anchor["state_after"])

    def test_traversing_configuration_does_not_touch_outside_file(self):
        workspace = new_workspace(self.case / "workspace", self.root)
        sentinel = self.case / "outside.sqlite"
        sentinel.write_bytes(b"KEEP")
        value = read_json(self.root / CONFIG)
        value["state_path"] = "../outside.sqlite"
        with self.config(value):
            result = self.service(workspace)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(sentinel.read_bytes(), b"KEEP")

    def test_symlink_state_directory_cannot_escape_owned_workspace(self):
        workspace = new_workspace(self.case / "workspace", self.root)
        outside = self.case / "outside"
        outside.mkdir()
        (workspace / "state").mkdir()
        (workspace / "state/control").symlink_to(outside, target_is_directory=True)
        result = self.service(workspace, self.root / REFERENCE_CONFIG)
        self.assertEqual(result["error"], "OWNED_PATH_SYMLINK")
        self.assertFalse(list(outside.iterdir()))

    def test_malformed_nested_config_fails_without_creating_database(self):
        workspace = new_workspace(self.case / "workspace", self.root)
        value = read_json(self.root / CONFIG)
        value["state_path"] = ["state/control/history.sqlite"]
        with self.config(value):
            result = self.service(workspace)
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(list(workspace.rglob("*.sqlite")))

    def test_changed_session_database_is_rejected_before_recovery(self):
        session = self.case / "session"
        shutil.copytree(self.session, session)
        with (session / "state/incident/history.sqlite").open("ab") as stream:
            stream.write(b"changed")
        result = evaluate_incident(session, self.root, reference=True, output=self.case / "review")
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("STALE_EVIDENCE:state/incident/history.sqlite" == finding for finding in result["findings"]))
        self.assertFalse((self.case / "review/steps").exists())

    def test_changed_raw_log_is_rejected(self):
        session = self.case / "session"
        shutil.copytree(self.session, session)
        (session / "steps/S06_fault_current.log").write_text("replaced log")
        result = evaluate_incident(session, self.root, reference=True, output=self.case / "review")
        self.assertIn("STALE_EVIDENCE:steps/S06_fault_current.log", result["findings"])

    def test_current_history_comment_invalidates_prior_session(self):
        with replaced(self.root / HISTORY, (self.root / REFERENCE_HISTORY).read_bytes()):
            session = self.case / "current_session"
            rehearse_incident(session, self.root)
            with replaced(self.root / HISTORY, (self.root / HISTORY).read_bytes() + b"\n# changed source identity\n"):
                result = evaluate_incident(session, self.root, output=self.case / "review")
        self.assertIn("STALE_SESSION_INPUT:" + HISTORY, result["findings"])

    def test_receipt_recheck_passes_without_reusing_old_output(self):
        result = self.gate(reference=True, receipt=self.reference_output / "INCIDENT_RESULT.json")
        self.assertEqual(result["status"], SUCCESS, result["findings"])

    def test_receipt_cannot_ignore_changed_evidence(self):
        previous = self.case / "prior"
        shutil.copytree(self.reference_output, previous)
        (previous / "state/control/history.sqlite").write_bytes(b"wrong")
        result = self.gate(reference=True, receipt=previous / "INCIDENT_RESULT.json")
        self.assertIn("STALE_EVIDENCE:state/control/history.sqlite", result["findings"])

    def test_malformed_receipt_fails_closed(self):
        receipt = self.case / "malformed_input/INCIDENT_RESULT.json"
        write_json(receipt, ["not a receipt"])
        result = self.gate(reference=True, receipt=receipt)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("RECEIPT_SCHEMA", result["findings"])

    def test_cp12_baseline_rejects_history_source_edit(self):
        baseline = self.case / "baseline.json"
        write_json(baseline, capture_edit_scope("CP12", self.root))
        with replaced(self.root / HISTORY, (self.root / HISTORY).read_bytes() + b"\n# forbidden in CP12\n"):
            result = self.gate(reference=True, scope_baseline=baseline)
        self.assertIn("OUT_OF_SCOPE:src/treasury/policy_history.py", result["findings"])
        self.assertFalse((self.case / "review/steps").exists())

    def test_protected_fixture_tamper_blocks_before_worker_execution(self):
        scenario = self.root / "reader_side/operations/scenario.json"
        with replaced(scenario, scenario.read_bytes() + b"\n"):
            result = self.gate(reference=True)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any(finding.startswith("PROTECTED_INTEGRITY:") for finding in result["findings"]))
        self.assertFalse((self.case / "review/steps").exists())

    def test_nested_output_cannot_mutate_rehearsal_evidence(self):
        before = tree_hashes(self.session)
        with self.assertRaisesRegex(ValueError, "OUTPUT_MUST_NOT_NEST"):
            evaluate_incident(self.session, self.root, reference=True, output=self.session / "nested_review")
        self.assertEqual(tree_hashes(self.session), before)

    def test_existing_cli_output_preserves_sentinel(self):
        output = self.case / "existing"
        output.mkdir()
        sentinel = output / "KEEP.txt"
        sentinel.write_text("KEEP")
        completed = subprocess.run([sys.executable, "-B", str(self.root / "reader_side/tools/incident_gate.py"),
                                   "--rehearsal", str(self.session), "--output", str(output), "--reference"],
                                  env=environment(), capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(sentinel.read_text(), "KEEP")


if __name__ == "__main__":
    unittest.main()
