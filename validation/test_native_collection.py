from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import observe_native as collect

spec = importlib.util.spec_from_file_location("diagnose_trace", HERE.parent / "practice/mcp_cli/diagnose_trace.py")
trace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trace)


class NativeCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"; self.source.mkdir()
        (self.source / "candidate.py").write_text("print('unchanged')\n")
        self.record_path = collect.prepare(self.source, self.root / "evidence", ["R06", "R07"])

    def fill_rehearsal(self):
        record = json.loads(self.record_path.read_text())
        record.update(execution_kind="OFFLINE_COLLECTOR_REHEARSAL",
                      prior_solution_exposure="Synthetic unit-test evidence only; no person or model observed.",
                      protocol_era="2026-07-28", boundary_scope="Synthetic canary record; no isolation claim.")
        record["client"] = {"name": "Synthetic test producer", "version": "test-1",
                            "model_identity": None, "model_identity_availability": "NOT_APPLICABLE_REHEARSAL"}
        self.record_path.write_text(json.dumps(record))
        for category in collect.R06_ARTIFACTS + collect.R07_ARTIFACTS:
            path = self.record_path.parent / (category + ".txt")
            path.write_text("Synthetic unit-test fixture: " + category + "\n")
            collect.bind(self.record_path, category, path.name)

    def test_complete_rehearsal_never_becomes_native_acceptance(self):
        self.fill_rehearsal()
        result = collect.inspect(self.record_path)
        self.assertEqual(result["status"], "PASS_REHEARSAL_EVIDENCE_CONSISTENCY")
        self.assertEqual(result["native_authenticity"], "NOT_ESTABLISHED_BY_THIS_CHECK")
        self.assertEqual(result["human_acceptance"], "NOT_GRANTED_BY_THIS_CHECK")

    def test_unfilled_packet_fails_instead_of_fabricating_a_run(self):
        result = collect.inspect(self.record_path)
        self.assertIn("NO_OBSERVED_EXECUTION_DECLARED", result["issues"])
        self.assertIn("MISSING_EVIDENCE:first_output", result["issues"])

    def test_modified_bound_file_is_detected(self):
        self.fill_rehearsal()
        (self.record_path.parent / "first_output.txt").write_text("rewritten first output")
        self.assertIn("EVIDENCE_HASH_MISMATCH:first_output", collect.inspect(self.record_path)["issues"])

    def test_modified_snapshot_is_detected(self):
        self.fill_rehearsal()
        (self.record_path.parent / "starting_tree/candidate.py").write_text("changed")
        self.assertIn("STARTING_TREE_MISSING_OR_CHANGED", collect.inspect(self.record_path)["issues"])

    def test_bound_category_cannot_replace_first_evidence(self):
        self.fill_rehearsal()
        with self.assertRaisesRegex(ValueError, "already bound"):
            collect.bind(self.record_path, "first_output", "final_diff.txt")

    def test_external_symlink_is_not_accepted_as_evidence(self):
        self.fill_rehearsal()
        path = self.record_path.parent / "first_output.txt"
        path.unlink(); path.symlink_to(self.source / "candidate.py")
        issues = collect.inspect(self.record_path)["issues"]
        self.assertTrue(any(item.startswith("INVALID_EVIDENCE:first_output") for item in issues))

    def test_output_and_snapshot_cannot_overwrite_source(self):
        with self.assertRaises(ValueError):
            collect.prepare(self.source, self.source / "evidence", ["R06"])
        with self.assertRaises(ValueError):
            collect.prepare(self.source, self.record_path.parent, ["R06"])
        self.assertEqual((self.source / "candidate.py").read_text(), "print('unchanged')\n")

    def test_unknown_native_identity_and_unobserved_selection_fail(self):
        self.fill_rehearsal()
        record = json.loads(self.record_path.read_text())
        record["execution_kind"] = "ACTUAL_NAMED_CLIENT"
        record["client"]["version"] = "UNKNOWN_NOT_EXPOSED"
        record["client"]["model_identity_availability"] = "NOT_EXPOSED"
        self.record_path.write_text(json.dumps(record))
        issues = collect.inspect(self.record_path)["issues"]
        self.assertIn("CLIENT_IDENTITY_MISSING:version", issues)
        self.assertIn("NATIVE_TOOL_SELECTION_UNOBSERVED", issues)

    def test_unobserved_contrast_cannot_claim_paired_performance(self):
        self.fill_rehearsal()
        record = json.loads(self.record_path.read_text())
        record["contrast"]["paired_performance_claim"] = True
        self.record_path.write_text(json.dumps(record))
        self.assertIn("UNOBSERVED_CONTRAST_CANNOT_SUPPORT_PERFORMANCE_CLAIM", collect.inspect(self.record_path)["issues"])

    def test_modern_era_needs_no_legacy_initialization_artifact(self):
        self.fill_rehearsal()
        result = collect.inspect(self.record_path)
        self.assertEqual(result["issues"], [])
        self.assertIn("mcp_opening_exchange", result["required_categories"])
        self.assertNotIn("initialization", result["required_categories"])


class TraceDiagnosisTests(unittest.TestCase):
    def test_actual_retained_pass_distinguishes_argument_and_domain(self):
        result = trace.diagnose(HERE.parent / "practice/mcp_cli/observed/attempt_02_local_stdio_pass")
        self.assertEqual(result["status"], "PASS_RETAINED_TRACE_DIAGNOSIS")
        self.assertEqual([item["classification"] for item in result["calls"]],
                         ["DOMAIN_SUCCESS", "DOMAIN_SUCCESS", "DOMAIN_REFUSAL", "SCHEMA_INVALID_ARGUMENT_REJECTED"])
        self.assertEqual(result["opening"]["methods"], ["server/discover"])

    def test_actual_retained_timeout_does_not_invent_a_cause(self):
        result = trace.diagnose(HERE.parent / "practice/mcp_cli/observed/attempt_01_restricted_timeout")
        self.assertEqual(result["opening"]["classification"], "NO_OPENING_RESPONSE_STARTUP_OR_TRANSPORT_UNRESOLVED")
        self.assertEqual(result["process_startup"], "NOT_PROVEN_BY_AN_UNANSWERED_REQUEST")

    def test_tampered_trace_is_rejected(self):
        source = HERE.parent / "practice/mcp_cli/observed/attempt_02_local_stdio_pass"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ["COMPARISON.json", "client_to_server.jsonl", "server_to_client.jsonl"]:
                (root / name).write_bytes((source / name).read_bytes())
            with (root / "server_to_client.jsonl").open("a") as stream:
                stream.write('{"jsonrpc":"2.0","id":"unretained","result":{}}\n')
            result = trace.diagnose(root)
            self.assertEqual(result["status"], "FAIL_TRACE_IDENTITY")
            self.assertIn("TRACE_IDENTITY_MISMATCH:server_to_client.jsonl", result["issues"])
            self.assertIn("UNSOLICITED_RESPONSE_ID", result["issues"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
