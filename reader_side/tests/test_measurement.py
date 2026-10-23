"""CP14 observed workflow and scenario boundaries; no invented field measurements."""
from contextlib import contextmanager
from decimal import Decimal
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from integration_core import INPUT_PAIRS
from incident_core import rehearse_incident
from learning_core import rehearse_transfer
from measurement_core import (REVIEW, DECISION, REFERENCE_REVIEW, REFERENCE_DECISION, COSTS, SUCCESS, RECORDED,
    rehearse_measurement, evaluate_measurement, measurement_checks, load_events, retained_acceptance,
    read_json, write_json, digest, canonical, tree_hashes)
from measurement_costs import nonnegative_decimal, cost_per_accepted, calculate_scenarios
from scope_guard import capture_edit_scope
from release_core import rehearse as rehearse_release, evaluate_release


@contextmanager
def replaced(path, raw):
    before = path.read_bytes()
    path.write_bytes(raw)
    try:
        yield
    finally:
        path.write_bytes(before)


class ScenarioCostTests(unittest.TestCase):
    def setUp(self):
        self.fixture = read_json(TOOLS.parents[1] / COSTS)
        self.ids = ["A01", "A02", "A03", "A04", "A05"]

    def test_exact_costs_include_failed_repeated_and_rework_attempts(self):
        result = calculate_scenarios(self.fixture, self.ids, 1)
        self.assertEqual([row["cost"] for row in result["attempt_costs"]], ["13.03", "11.04", "2.52", "4.52", "6.53"])
        self.assertEqual(result["total_cost"], "37.64")
        self.assertEqual(result["labor_costs"], {"initial": "8.00", "review": "17.50", "rework": "12.00"})

    def test_conditional_go_change_stop_and_zero_denominator(self):
        rows = calculate_scenarios(self.fixture, self.ids, 1)["scenarios"]
        self.assertEqual([row["conditional_pilot_decision"] for row in rows], ["GO", "CHANGE", "STOP"])
        self.assertEqual(rows[1]["total_cost"], "57.64")
        self.assertEqual(rows[2]["cost_per_accepted_outcome"]["status"], "UNDEFINED")
        self.assertIsNone(rows[2]["cost_per_accepted_outcome"]["amount"])
        self.assertEqual(rows[2]["total_cost"], "37.64")

    def test_decimal_rejects_nonfinite_negative_exponent_boolean_and_float(self):
        for value in ("NaN", "Infinity", "-1", "1e2", True, 0.1, None, "1000000001", "0.0000001"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                nonnegative_decimal(value, "test")

    def test_total_and_denominator_boundaries_fail_closed(self):
        for total, count, currency in ((Decimal("NaN"), 1, "EUR"), (Decimal("-1"), 1, "EUR"),
                                       (Decimal(1), True, "EUR"), (Decimal(1), -1, "EUR"), (Decimal(1), 1, "USD")):
            with self.subTest(total=total, count=count, currency=currency), self.assertRaises(ValueError):
                cost_per_accepted(total, count, currency)
        self.assertIsNone(cost_per_accepted(Decimal("5"), 0, "EUR")["amount"])

    def test_missing_or_duplicate_attempt_cost_is_rejected(self):
        for mutation in (lambda rows: rows.pop(), lambda rows: rows.__setitem__(1, rows[0])):
            fixture = json.loads(json.dumps(self.fixture))
            mutation(fixture["attempt_costs"])
            with self.assertRaises(ValueError):
                calculate_scenarios(fixture, self.ids, 1)

    def test_currency_mixing_and_missing_hours_are_not_zero(self):
        for key, value in (("currency", "USD"), ("review_hours", None)):
            fixture = json.loads(json.dumps(self.fixture))
            fixture["attempt_costs"][0][key] = value
            with self.assertRaises(ValueError):
                calculate_scenarios(fixture, self.ids, 1)

    def test_rates_and_sensitivity_boolean_schema_are_strict(self):
        fixture = json.loads(json.dumps(self.fixture))
        fixture["scenarios"][0]["retain_final_acceptance"] = 1
        with self.assertRaisesRegex(ValueError, "SENSITIVITY_SCHEMA"):
            calculate_scenarios(fixture, self.ids, 1)
        fixture = json.loads(json.dumps(self.fixture))
        fixture["rates_per_hour"]["review"] = "NaN"
        with self.assertRaises(ValueError):
            calculate_scenarios(fixture, self.ids, 1)

    def test_currency_rounding_is_explicit_not_binary_float(self):
        self.assertEqual(cost_per_accepted(Decimal("1.005"), 1, "EUR")["amount"], "1.01")
        self.assertEqual(cost_per_accepted(Decimal("1.00"), 3, "EUR")["amount"], "0.33")


class MeasurementWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="cp14-focused-")
        cls.directory = Path(cls.temporary.name)
        cls.root = cls.directory / "companion"
        shutil.copytree(TOOLS.parents[1], cls.root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "evidence"))
        pairs = list(INPUT_PAIRS.values()) + [
            ("repo/src/treasury/policy_history.py", "reader_side/reference_solution/ch11/policy_history.py"),
            ("repo/engineering/evolution/policy_delta.json", "reader_side/reference_solution/ch11/policy_delta.json"),
            ("repo/engineering/operations/deployment.json", "reader_side/reference_solution/ch12/deployment.json"),
            ("repo/engineering/operations/incident_review.json", "reader_side/reference_solution/ch12/incident_review.json"),
            ("repo/engineering/learning/transfer_review.json", "reader_side/reference_solution/ch13/transfer_review.json"),
            ("repo/engineering/learning/team_knowledge.json", "reader_side/reference_solution/ch13/team_knowledge.json")]
        for candidate, reference in pairs:
            (cls.root / candidate).write_bytes((cls.root / reference).read_bytes())
        cls.incident, cls.transfer, cls.session = (cls.directory / name for name in ("current_incident", "current_transfer", "current_measurement"))
        rehearse_incident(cls.incident, cls.root)
        rehearse_transfer(cls.incident, cls.transfer, cls.root)
        cls.rehearsal = rehearse_measurement(cls.incident, cls.transfer, cls.session, cls.root)
        cls.reference_incident, cls.reference_transfer, cls.reference_session = (cls.directory / name for name in
            ("reference_incident", "reference_transfer", "reference_measurement"))
        rehearse_incident(cls.reference_incident, cls.root, reference=True)
        rehearse_transfer(cls.reference_incident, cls.reference_transfer, cls.root, reference=True)
        cls.reference_rehearsal = rehearse_measurement(cls.reference_incident, cls.reference_transfer, cls.reference_session, cls.root, reference=True)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.case = self.directory / self._testMethodName
        self.case.mkdir()

    def copy_session(self):
        destination = self.case / "session"
        shutil.copytree(self.session, destination)
        return destination

    def test_current_process_workflow_records_all_attempts_and_two_A04_commands(self):
        self.assertEqual(self.rehearsal["status"], RECORDED, self.rehearsal["findings"])
        events = [v for v in load_events(self.session) if v["kind"] == "COMMAND"]
        self.assertEqual([v["attempt_id"] for v in events], ["A01", "A02", "A03", "A04", "A04", "A05"])
        self.assertTrue(all(type(v["elapsed_ns"]) is int and v["elapsed_ns"] > 0 for v in events))
        self.assertTrue(all(row["passed"] for row in self.rehearsal["checks"]))

    def test_distinct_acceptance_is_one_not_three_green_attempts(self):
        telemetry = self.rehearsal["local_telemetry"]
        self.assertEqual(telemetry["machine_green_attempts"], 3)
        self.assertEqual(telemetry["gate_attempts"], 5)
        self.assertEqual(self.rehearsal["scenario_acceptance"]["count"], 1)
        self.assertEqual(self.rehearsal["scenario_acceptance"]["accepted_attempt"], "A05")

    def test_actual_hours_billing_acceptance_and_cost_stay_unknown(self):
        for key in ("actual_human_effort_hours", "actual_vendor_billing", "actual_human_accepted_outcomes", "actual_cost_per_accepted_outcome"):
            self.assertIsNone(self.rehearsal["local_telemetry"][key])

    def test_seed_and_final_transfer_are_distinct_and_bind_same_CP12(self):
        self.assertNotEqual(self.rehearsal["seed_transfer_session_sha256"], self.rehearsal["final_transfer_session_sha256"])
        for path in (self.session / "inputs/transfer", self.session / "refreshed_transfer"):
            self.assertEqual(read_json(path / "TRANSFER_SESSION.json")["learning_session_sha256"], self.rehearsal["incident_session_sha256"])
        stale = read_json(self.session / "attempts/A04/LEARNING_RESULT.json")
        self.assertIn("STALE_RECEIPT_SESSION", stale["findings"])

    def test_reference_and_stable_unsafe_controls_work_after_current_repairs(self):
        self.assertEqual(self.reference_rehearsal["status"], RECORDED, self.reference_rehearsal["findings"])
        with replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()), \
             replaced(self.root / DECISION, (self.root / REFERENCE_DECISION).read_bytes()):
            safe = evaluate_measurement(self.reference_session, self.root, reference=True, output=self.case / "safe")
            unsafe = evaluate_measurement(self.reference_session, self.root, unsafe=True, output=self.case / "unsafe")
        self.assertEqual(safe["status"], SUCCESS, safe["findings"])
        self.assertEqual(unsafe["status"], "FAIL")
        self.assertIn("OUTCOME_REVIEW:distinct_synthetic_accepted_outcomes", unsafe["findings"])

    def test_current_CP14_repair_obeys_scope_and_does_not_stale_measurement(self):
        baseline = self.case / "baseline.json"
        write_json(baseline, capture_edit_scope("CP14", self.root))
        with replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()), \
             replaced(self.root / DECISION, (self.root / REFERENCE_DECISION).read_bytes()):
            result = evaluate_measurement(self.session, self.root, output=self.case / "review", scope_baseline=baseline)
        self.assertEqual(result["status"], SUCCESS, result["findings"])
        self.assertEqual(result["actual_pilot_decision"], "CHANGE")
        self.assertIs(result["authority"]["real_release_authorized"], False)

    def test_reference_session_cannot_certify_current_candidates(self):
        result = evaluate_measurement(self.reference_session, self.root, output=self.case / "review")
        self.assertIn("MEASUREMENT_STATUS_OR_MODE", result["findings"])

    def test_changed_upstream_learning_source_stales_measurement(self):
        path = self.root / "repo/engineering/learning/team_knowledge.json"
        with replaced(path, path.read_bytes() + b"\n"):
            result = evaluate_measurement(self.session, self.root, output=self.case / "review")
        self.assertIn("STALE_MEASUREMENT_INPUT:repo/engineering/learning/team_knowledge.json", result["findings"])

    def test_CP13_edit_is_outside_CP14_scope(self):
        baseline = self.case / "baseline.json"
        write_json(baseline, capture_edit_scope("CP14", self.root))
        path = self.root / "repo/engineering/learning/team_knowledge.json"
        with replaced(path, path.read_bytes() + b"\n"):
            result = evaluate_measurement(self.session, self.root, output=self.case / "review", scope_baseline=baseline)
        self.assertIn("OUT_OF_SCOPE:engineering/learning/team_knowledge.json", result["findings"])

    def test_deleted_attempt_and_broken_raw_chain_fail_closed(self):
        session = self.copy_session()
        (session / "raw/000002.json").unlink()
        with self.assertRaisesRegex(ValueError, "RAW_EVENT_SEQUENCE"):
            load_events(session)

    def test_clock_fields_are_recomputed_instead_of_trusting_elapsed_claim(self):
        session = self.copy_session()
        files = sorted((session / "raw").glob("*.json"))
        previous = None
        for path in files:
            value = read_json(path)
            if value.get("command_id") == "C01":
                value["elapsed_ns"] += 1
            value["previous_sha256"] = previous
            write_json(path, value)
            previous = digest(path)
        checks, _, _ = measurement_checks(session, self.root)
        self.assertFalse(next(row["passed"] for row in checks if row["name"] == "C01:observed_clock_only"))

    def test_stale_first_green_cannot_replace_final_acceptance(self):
        session = self.copy_session()
        value = read_json(session / "SYNTHETIC_OWNER_ACCEPTANCE.json")
        value["accepted_attempt"] = "A02"
        value["receipt_sha256"] = digest(session / "attempts/A02/LEARNING_RESULT.json")
        write_json(session / "SYNTHETIC_OWNER_ACCEPTANCE.json", value)
        with self.assertRaisesRegex(ValueError, "SYNTHETIC_ACCEPTANCE"):
            retained_acceptance(session, self.root, False)

    def test_acceptance_artifact_substitution_and_human_relabel_rejected(self):
        for field, value in (("artifact_sha256", "0" * 64), ("real_human_acceptance", True)):
            with self.subTest(field=field):
                before = (self.session / "SYNTHETIC_OWNER_ACCEPTANCE.json").read_bytes()
                record = json.loads(before)
                record[field] = value
                with replaced(self.session / "SYNTHETIC_OWNER_ACCEPTANCE.json", (json.dumps(record) + "\n").encode()):
                    with self.assertRaisesRegex(ValueError, "SYNTHETIC_ACCEPTANCE"):
                        retained_acceptance(self.session, self.root, False)

    def test_raw_log_tamper_is_detected_before_scenario_calculation(self):
        session = self.copy_session()
        (session / "logs/C01.stdout.log").write_text("changed")
        result = evaluate_measurement(session, self.root, output=self.case / "review")
        self.assertIn("STALE_EVIDENCE:logs/C01.stdout.log", result["findings"])
        self.assertNotIn("scenario_costs", result)

    def test_protected_cost_oracle_tamper_blocks_accounting(self):
        path = self.root / COSTS
        with replaced(path, path.read_bytes() + b"\n"):
            result = evaluate_measurement(self.session, self.root, output=self.case / "review")
        self.assertIn("PROTECTED_INTEGRITY:" + COSTS, result["findings"])
        self.assertEqual(result["checks"], [])

    def test_receipt_freshness_and_candidate_comment_change(self):
        with replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()), \
             replaced(self.root / DECISION, (self.root / REFERENCE_DECISION).read_bytes()):
            first = self.case / "first"
            self.assertEqual(evaluate_measurement(self.session, self.root, output=first)["status"], SUCCESS)
            receipt = first / "MEASUREMENT_RESULT.json"
            self.assertEqual(evaluate_measurement(self.session, self.root, output=self.case / "fresh", receipt=receipt)["status"], SUCCESS)
            with replaced(self.root / DECISION, (self.root / DECISION).read_bytes() + b"\n"):
                stale = evaluate_measurement(self.session, self.root, output=self.case / "stale", receipt=receipt)
        self.assertIn("STALE_RECEIPT:" + DECISION, stale["findings"])

    def test_existing_output_is_preserved(self):
        path = self.case / "prior"
        path.mkdir()
        (path / "sentinel").write_text("retain")
        with self.assertRaises(FileExistsError):
            evaluate_measurement(self.session, self.root, output=path)
        self.assertEqual((path / "sentinel").read_text(), "retain")

    def test_field_template_is_unfilled_and_not_synthetic_measurement(self):
        template = read_json(self.root / "reader_side/measurement/FIELD_TELEMETRY_TEMPLATE.json")
        self.assertEqual(template["status"], "UNFILLED_FUTURE_TEMPLATE")
        for key in ("effort_records", "billing_records", "owner_outcome_records"):
            self.assertEqual(template[key], [])
        self.assertTrue(template["missingness_records"])

    def test_vendor_capability_docs_do_not_claim_live_comparison(self):
        matrix = read_json(self.root / "reader_side/measurement/tool_capabilities.json")
        for row in matrix["options"]:
            self.assertEqual(row["live_comparative_benchmark"], "UNKNOWN")
            if row["id"] != "LOCAL-CONTROL":
                self.assertEqual(row["tested_status"], "DOCUMENTED_NOT_EXECUTED")
                self.assertTrue(row["primary_urls"])

    def test_CP14_repairs_stale_prior_CP10_receipts_in_completed_workspaces(self):
        with replaced(self.root / REVIEW, (self.root / "reader_side/measurement/unsafe_outcome_review.json").read_bytes()), \
             replaced(self.root / DECISION, (self.root / "reader_side/measurement/unsafe_tool_decision.json").read_bytes()):
            session = self.case / "earlier_release"
            self.assertEqual(rehearse_release(session, root=self.root)["status"], "READY_FOR_DOSSIER_REVIEW")
            dossier = self.root / "reader_side/reference_solution/ch10/release_dossier.json"
            before = evaluate_release(dossier, session, self.root)
            self.assertEqual(before["status"], "PASS_LOCAL_RELEASE_REHEARSAL_ONLY", before["findings"])
            with replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()), \
                 replaced(self.root / DECISION, (self.root / REFERENCE_DECISION).read_bytes()):
                after = evaluate_release(dossier, session, self.root)
        for name in (REVIEW, DECISION):
            self.assertIn("STALE_INPUT:" + name, after["findings"])


if __name__ == "__main__":
    unittest.main()
