"""Negative controls for the independent SDD artifact checker, not model tests."""
from pathlib import Path
import json
import shutil
import tempfile
import unittest

import check


class ArtifactFidelityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "artifacts"
        shutil.copytree(check.PRACTICE / "fixtures/after", self.root)
        self.addCleanup(self.temp.cleanup)

    def replace(self, old, new, flow="speckit", role="spec"):
        path = self.root / flow / check.FILES[flow][role]
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def issues(self, flow="speckit"):
        return next(r["issues"] for r in check.compare(self.root)["flows"] if r["flow"] == flow)

    def test_repaired_specs_satisfy_fixed_obligations(self):
        report = check.compare(self.root)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["pair_case_values_equal"])
        self.assertEqual(report["human_review"], "pending")

    def test_equal_incomplete_specs_still_fail_independent_oracle(self):
        report = check.compare(check.PRACTICE / "fixtures/before")
        self.assertTrue(report["pair_case_values_equal"])
        self.assertEqual(report["status"], "FAIL")
        for flow in report["flows"]:
            self.assertEqual(flow["issues"], ["MISSING_CASE:SC-EXPL-002"])

    def test_wrong_equality_route_is_rejected(self):
        marker = "amount_eur = `5000`\n- **THEN** route = `HUMAN_REVIEW`"
        self.replace(marker, marker.replace("HUMAN_REVIEW", "STANDARD_QUEUE"))
        self.assertIn("CASE_VALUE_MISMATCH:SC-EXPL-002:expected_route", self.issues())

    def test_payment_approval_cannot_hide_in_a_case(self):
        self.replace("payment_authorized = `false`", "payment_authorized = `true`")
        self.assertIn("CASE_VALUE_MISMATCH:SC-EXPL-001:payment_authorized", self.issues())

    def test_agreeing_wrong_outputs_do_not_become_truth(self):
        for flow in check.FILES:
            self.replace("reason = `BELOW_LIMIT`", "reason = `AUTO_APPROVED`", flow)
        report = check.compare(self.root)
        self.assertTrue(report["pair_case_values_equal"])
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(all("CASE_VALUE_MISMATCH:SC-EXPL-001:expected_reason" in f["issues"] for f in report["flows"]))

    def test_policy_authority_cannot_be_replaced_by_sponsor_ticket(self):
        self.replace("Policy authority: SRC-POL-001", "Policy authority: SRC-TKT-017")
        self.assertIn("CONTRACT_METADATA_MISMATCH:Policy authority", self.issues())

    def test_obligation_negation_change_is_detected(self):
        self.replace("MUST NOT silently infer", "MUST silently infer")
        self.assertIn("FIXED_OBLIGATION_WORDING_CHANGED:REQ-EXPL-004", self.issues())

    def test_requirement_source_loss_is_detected(self):
        self.replace("Sources: SRC-POL-001, SRC-RISK-002", "Sources: SRC-POL-001")
        self.assertIn("REQUIREMENT_SOURCE_OR_OWNER_MISMATCH:REQ-EXPL-002", self.issues())

    def test_duplicate_case_is_detected(self):
        self.replace("#### Scenario: SC-EXPL-002", "#### Scenario: SC-EXPL-001")
        self.assertIn("DUPLICATE_CASE:SC-EXPL-001", self.issues())

    def test_plan_must_trace_every_obligation(self):
        self.replace("REQ-EXPL-005", "benefit", role="plan")
        self.assertIn("OBLIGATION_TRACE_MISSING:plan:REQ-EXPL-005", self.issues())

    def test_unperformed_human_review_cannot_be_ticked_done(self):
        self.replace("- [ ] T01", "- [x] T01", role="tasks")
        self.assertIn("UNOBSERVED_HUMAN_REVIEW_MARKED_COMPLETE", self.issues())

    def test_origin_cannot_claim_a_model_trial(self):
        path = self.root / "speckit/ORIGIN.json"
        origin = json.loads(path.read_text()); origin["named_agent_execution"] = True
        path.write_text(json.dumps(origin))
        self.assertIn("EXERCISE_ORIGIN_MISREPRESENTED", self.issues())

    def test_symlinked_spec_is_rejected(self):
        path = self.root / "speckit/spec.md"
        target = path.with_name("external.md"); path.rename(target); path.symlink_to(target)
        self.assertTrue(any(i.startswith("ARTIFACT_UNREADABLE:spec:symlinked") for i in self.issues()))

    def test_altered_shared_manifest_is_detected(self):
        shared = Path(self.temp.name) / "shared"
        shutil.copytree(check.PRACTICE / "shared", shared)
        path = shared / "INPUT_MANIFEST.json"
        path.write_text(path.read_text() + "\n")
        self.assertEqual(check.shared_issues(shared), ["SHARED_MANIFEST_CHANGED"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
