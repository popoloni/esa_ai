"""Two different correct CP08 programs can complete CP10 technical learning.

All candidate edits and Git rehearsals happen in disposable copies. Existing
protected source, owner decisions and release checks remain unchanged.
"""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "reader_side/tools"))
import release_core as release
from complete_technical_learning import evaluate_completion, SUCCESS
from scope_guard import capture_edit_scope


ALTERNATIVE_A = '''"""Authored alternative: construct a label from a checked route."""
from treasury.architecture.direct import explain

def build_explanation(amount_eur: str) -> dict:
    result = dict(explain(amount_eur))
    route = result["route"]
    result["status_label"] = "REJECTED" if route == "REJECTED" else "RECOMMENDED_" + route
    return result
'''

ALTERNATIVE_B = '''"""Authored alternative: explicit label selection and field projection."""
from treasury.architecture.direct import explain

def build_explanation(amount_eur: str) -> dict:
    decision = explain(amount_eur)
    if decision["route"] == "STANDARD_QUEUE":
        label = "RECOMMENDED_STANDARD_QUEUE"
    elif decision["route"] == "HUMAN_REVIEW":
        label = "RECOMMENDED_HUMAN_REVIEW"
    else:
        label = "REJECTED"
    result = {name: decision[name] for name in (
        "route", "reason_code", "policy_version", "payment_authorized",
        "notice", "benefit_status")}
    result["status_label"] = label
    return result
'''


class TechnicalCompletionTests(unittest.TestCase):
    observations = {}

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="cp10-learning-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.base = Path(cls.temporary.name)
        cls.root = cls.base / "companion"
        for relative in release.source_manifest(ROOT):
            destination = cls.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / relative).read_bytes())
        for candidate, reference in release.INPUT_PAIRS.values():
            (cls.root / candidate).write_bytes((cls.root / reference).read_bytes())
        cls.original_source = (cls.root / release.PRODUCER).read_bytes()
        cls.safe_dossier = release.read_json(cls.root / release.REFERENCE)
        cls.baseline = cls.base / "CP10_EDIT_BASELINE.json"
        release.write_json(cls.baseline, capture_edit_scope("CP10", root=cls.root))
        cls.session = cls.base / "original_source_session"
        cls.record = release.rehearse(cls.session, root=cls.root)
        if cls.record["status"] != "READY_FOR_DOSSIER_REVIEW":
            raise AssertionError(cls.record)
        cls.protected_before = {
            name: release.digest(cls.root / name)
            for name in ["reader_side/protected_sha256.json",
                         "reader_side/tools/release_core.py",
                         *["reader_side/release/" + name for name in release.OWNER_FILES]]
        }

    def setUp(self):
        (self.root / release.PRODUCER).write_bytes(self.original_source)
        release.write_json(self.root / release.DOSSIER, self.safe_dossier)

    def tearDown(self):
        (self.root / release.PRODUCER).write_bytes(self.original_source)
        for name, expected in self.protected_before.items():
            self.assertEqual(expected, release.digest(self.root / name), name)

    def completion(self, session=None, baseline=None):
        return evaluate_completion(session or self.session, baseline or self.baseline,
                                   root=self.root)

    def change_dossier(self, **fields):
        value = dict(self.safe_dossier)
        value.update(fields)
        release.write_json(self.root / release.DOSSIER, value)

    def test_original_authorized_source_keeps_original_release_disposition(self):
        result = self.completion()
        self.assertEqual(SUCCESS, result["status"], result)
        self.assertEqual(release.SUCCESS, result["release_assessment"]["status"])
        self.observations["original_authorized_source"] = result

    def test_two_different_correct_implementations_complete_without_release(self):
        hashes = set()
        for name, source in (("alternative_a", ALTERNATIVE_A), ("alternative_b", ALTERNATIVE_B)):
            with self.subTest(implementation=name):
                (self.root / release.PRODUCER).write_text(source)
                source_hash = release.digest(self.root / release.PRODUCER)
                hashes.add(source_hash)
                self.assertNotEqual(release.digest(self.root / "reader_side/reference_solution/explanation_alpha.py"), source_hash)
                baseline = self.base / (name + "_CP10_BASELINE.json")
                release.write_json(baseline, capture_edit_scope("CP10", root=self.root))
                self.change_dossier(candidate_source_sha256=source_hash,
                                    review_decision_id=None, release_decision_id=None)
                session = self.base / name
                rehearsal = release.rehearse(session, root=self.root)
                self.assertEqual("READY_FOR_DOSSIER_REVIEW", rehearsal["status"], rehearsal)
                result = self.completion(session, baseline)
                self.assertEqual(SUCCESS, result["status"], result)
                gate = result["release_assessment"]
                self.assertEqual("PASS", gate["ci_status"])
                self.assertEqual("FAIL", gate["status"])
                self.assertEqual("NOT_AUTHORIZED", gate["local_release_decision"])
                self.assertIn("SOURCE_NOT_COVERED_BY_SYNTHETIC_OWNER_DECISION", gate["findings"])
                self.assertFalse(result["real_human_acceptance"])
                self.assertFalse(result["real_release_authorized"])
                self.observations[name] = {
                    "source": source, "source_sha256": source_hash,
                    "completion": result,
                    "checks": {key: release.read_json(session / value)
                               for key, value in release.CHECK_FILES.items()},
                    "rollback": rehearsal["rollback"],
                }
        self.assertEqual(2, len(hashes))

    def test_stale_source_does_not_complete(self):
        (self.root / release.PRODUCER).write_bytes(self.original_source + b"\n# Later edit.\n")
        result = self.completion()
        self.assertEqual("TECHNICAL_LEARNING_INCOMPLETE", result["status"])
        self.assertIn("STALE_INPUT:" + release.PRODUCER, result["findings"])
        self.assertEqual("FAIL", result["release_assessment"]["status"])
        self.observations["stale_source"] = result

    def test_missing_decisions_still_refuse_release(self):
        self.change_dossier(review_decision_id=None, release_decision_id=None)
        result = self.completion()
        self.assertEqual(SUCCESS, result["status"])
        gate = result["release_assessment"]
        self.assertEqual("FAIL", gate["status"])
        self.assertEqual("NOT_AUTHORIZED", gate["local_release_decision"])
        self.assertIn("REVIEW_DECISION_MISSING", gate["findings"])
        self.assertIn("EXPLICIT_LOCAL_RELEASE_AUTHORIZATION_MISSING", gate["findings"])
        self.observations["missing_decisions"] = result

    def test_self_issued_decision_completes_neither_route(self):
        self.change_dossier(review_decision_id="REVIEW-10-SELF")
        result = self.completion()
        self.assertEqual("TECHNICAL_LEARNING_INCOMPLETE", result["status"])
        self.assertIn("SELF_APPROVAL", result["findings"])
        self.assertEqual("FAIL", result["release_assessment"]["status"])
        self.observations["self_approval"] = result

    def test_omitted_fields_are_not_explicit_unissued_decisions(self):
        value = dict(self.safe_dossier)
        value.pop("review_decision_id")
        value.pop("release_decision_id")
        release.write_json(self.root / release.DOSSIER, value)
        result = self.completion()
        self.assertEqual("TECHNICAL_LEARNING_INCOMPLETE", result["status"])
        self.assertIn("REVIEW_DECISION_MISSING", result["findings"])

    def test_wrong_dossier_identity_does_not_complete(self):
        self.change_dossier(candidate_source_sha256="0" * 64)
        result = self.completion()
        self.assertEqual("TECHNICAL_LEARNING_INCOMPLETE", result["status"])
        self.assertIn("DOSSIER_SOURCE_IDENTITY", result["findings"])

    def test_missing_before_edit_baseline_does_not_complete(self):
        result = evaluate_completion(self.session, None, root=self.root)
        self.assertEqual("TECHNICAL_LEARNING_INCOMPLETE", result["status"])
        self.assertIn("BEFORE_EDIT_SCOPE_BASELINE_REQUIRED", result["findings"])

    def test_reference_rehearsal_does_not_complete_learner_work(self):
        session = self.base / "reference_session"
        record = release.rehearse(session, root=self.root, reference=True)
        self.assertEqual("READY_FOR_DOSSIER_REVIEW", record["status"])
        result = self.completion(session)
        self.assertEqual("TECHNICAL_LEARNING_INCOMPLETE", result["status"])
        self.assertIn("CURRENT_WORKING_CANDIDATES_REQUIRED", result["findings"])

    def test_incorrect_behavior_does_not_complete(self):
        source = ALTERNATIVE_A.replace('"RECOMMENDED_" + route', '"APPROVED_PAYMENT"')
        (self.root / release.PRODUCER).write_text(source)
        baseline = self.base / "bad_behavior_baseline.json"
        release.write_json(baseline, capture_edit_scope("CP10", root=self.root))
        self.change_dossier(candidate_source_sha256=release.digest(self.root / release.PRODUCER),
                            review_decision_id=None, release_decision_id=None)
        session = self.base / "bad_behavior_session"
        record = release.rehearse(session, root=self.root)
        self.assertEqual("FAIL", record["status"])
        result = self.completion(session, baseline)
        self.assertEqual("TECHNICAL_LEARNING_INCOMPLETE", result["status"])
        self.assertEqual("FAIL", result["release_assessment"]["status"])
        self.observations["incorrect_behavior"] = result

    def test_cli_preserves_an_existing_receipt(self):
        output = self.base / "previous_completion.json"
        sentinel = b'{"previous_observation":"preserve"}\n'
        output.write_bytes(sentinel)
        completed = subprocess.run([sys.executable, "-B",
            str(self.root / "reader_side/tools/complete_technical_learning.py"),
            "--rehearsal", str(self.session), "--scope-baseline", str(self.baseline),
            "--output", str(output)], cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertEqual(sentinel, output.read_bytes())
        self.assertEqual("", completed.stdout)


if __name__ == "__main__":
    unittest.main()
