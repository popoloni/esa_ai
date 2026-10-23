"""CP13 process/protocol checks; every injected clock and rater is synthetic."""
from contextlib import contextmanager
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from integration_core import INPUT_PAIRS
from incident_core import rehearse_incident, environment
from learning_core import (REVIEW, KNOWLEDGE, REFERENCE_REVIEW, REFERENCE_KNOWLEDGE, HISTORY,
    REFERENCE_HISTORY, SUCCESS, TRANSFER_SUCCESS, rehearse_transfer, evaluate_learning,
    read_json, write_json, digest, tree_hashes, affected_claims)
from learning_pilot_core import (SYNTHETIC, HUMAN, checked_clock, owner_clock, start_trial,
    submit_answer, release_retention, release_transfer, record_score, adjudicate, pilot_status)
from scope_guard import capture_edit_scope
from release_core import rehearse as rehearse_release, evaluate_release


@contextmanager
def replaced(path, content):
    old = path.read_bytes()
    path.write_bytes(content if isinstance(content, bytes) else content.encode())
    try:
        yield
    finally:
        path.write_bytes(old)


class LearningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="cp13-focused-")
        cls.directory = Path(cls.temporary.name)
        cls.root = cls.directory / "companion"
        shutil.copytree(TOOLS.parents[1], cls.root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "evidence"))
        pairs = list(INPUT_PAIRS.values()) + [
            (HISTORY, REFERENCE_HISTORY),
            ("repo/engineering/evolution/policy_delta.json", "reader_side/reference_solution/ch11/policy_delta.json"),
            ("repo/engineering/operations/deployment.json", "reader_side/reference_solution/ch12/deployment.json"),
            ("repo/engineering/operations/incident_review.json", "reader_side/reference_solution/ch12/incident_review.json")]
        for target, reference in pairs:
            (cls.root / target).write_bytes((cls.root / reference).read_bytes())
        cls.learning = cls.directory / "learning_reference"
        rehearse_incident(cls.learning, cls.root, reference=True)
        cls.transfer = cls.directory / "transfer_reference"
        cls.transfer_result = rehearse_transfer(cls.learning, cls.transfer, cls.root, reference=True)
        cls.good_dir = cls.directory / "good_review"
        cls.good = evaluate_learning(cls.transfer, cls.root, reference=True, output=cls.good_dir)
        cls.current_learning = cls.directory / "learning_current"
        rehearse_incident(cls.current_learning, cls.root)
        cls.current_transfer = cls.directory / "transfer_current"
        rehearse_transfer(cls.current_learning, cls.current_transfer, cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.case = self.directory / self._testMethodName
        self.case.mkdir()
        self.tick = 0
        self.owner, self.trial = self.case / "owner", self.case / "public"

    def clock(self, seconds=1):
        self.tick += seconds * 1_000_000_000
        return {"kind": "PROTECTED_SYNTHETIC_CLOCK", "wall_ns": 1_800_000_000_000_000_000 + self.tick,
                "monotonic_ns": 1_000_000_000 + self.tick, "host_boot": "SYNTHETIC_TEST_CONTEXT"}

    def start(self):
        return start_trial(self.transfer, self.owner, self.trial, "synthetic_learner", ["synthetic_a", "synthetic_b"],
                           "synthetic_coordinator", True, self.root, synthetic=True, clock=self.clock())

    def answer(self, task):
        path = self.case / (task + ".md")
        path.write_text("Synthetic raw explanation with no machine-scored keywords.\n")
        return submit_answer(self.owner, task, path, self.root, self.clock())

    def ready_for_reviews(self):
        self.start()
        self.assertTrue((self.trial / "baseline_prompt.md").is_file())
        self.assertFalse((self.trial / "team_knowledge.json").exists())
        self.answer("baseline")
        release_retention(self.owner, self.root, self.clock(86400))
        self.answer("retention")
        release_transfer(self.owner, self.root, self.clock())
        self.answer("transfer")

    def form(self, reviewer, value=2):
        form = read_json(self.trial / "review_forms" / (reviewer + ".json"))
        for task in form["ratings"]:
            form["ratings"][task] = {key: value for key in form["ratings"][task]}
            form["rationales"][task] = "Synthetic rater declaration only, not a human judgment."
        path = self.case / (reviewer + ".json")
        write_json(path, form)
        return path

    def test_actual_transfer_case_requires_a_different_diagnosis(self):
        self.assertEqual(self.transfer_result["status"], TRANSFER_SUCCESS, self.transfer_result["findings"])
        checks = {row["name"]: row["passed"] for row in self.transfer_result["checks"]}
        for name in ("same_existing_ledger_and_source", "observed_activation_is_audited",
                     "fresh_request_and_retained_retry_differ", "path_recipe_does_not_restore_active_policy",
                     "recovery_retains_all_fault_history", "fault_state_preserved_after_recovery"):
            self.assertIs(checks[name], True)

    def test_reference_pass_leaves_human_trial_and_validity_pending(self):
        self.assertEqual(self.good["status"], SUCCESS, self.good["findings"])
        self.assertEqual(self.good["human_delay_trial"], "PENDING")
        self.assertEqual(self.good["rubric_validity"], "PENDING_HUMAN_VALIDATION")
        self.assertEqual(self.good["human_competence"], "NOT_ESTABLISHED_BY_AUTOMATION")
        self.assertIs(self.good["authority"]["real_release_authorized"], False)

    def test_synthetic_calibration_retains_raw_disagreement_and_separate_adjudication(self):
        result = read_json(self.good_dir / "synthetic_calibration/CALIBRATION_RESULT.json")
        self.assertEqual(result["status"], "PASS_SYNTHETIC_CALIBRATION_ONLY")
        self.assertTrue(all(row["passed"] for row in result["checks"]))
        self.assertTrue(result["pilot_status"]["disagreements"])
        self.assertIn("separate_adjudication", result["pilot_status"])
        self.assertIs(result["pilot_status"]["real_clock_delay_elapsed"], False)
        self.assertFalse(list((self.good_dir / "synthetic_calibration").rglob("owner.key")))

    def test_unsafe_control_survives_current_candidate_repair(self):
        with replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()), \
             replaced(self.root / KNOWLEDGE, (self.root / REFERENCE_KNOWLEDGE).read_bytes()):
            result = evaluate_learning(self.transfer, self.root, unsafe=True, output=self.case / "review")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("TRANSFER_REVIEW:root_cause", result["findings"])
        self.assertIn("TEAM_KNOWLEDGE:claim_dependencies", result["findings"])

    def test_current_repair_obeys_actual_cp13_scope(self):
        baseline = self.case / "baseline.json"
        write_json(baseline, capture_edit_scope("CP13", self.root))
        with replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()), \
             replaced(self.root / KNOWLEDGE, (self.root / REFERENCE_KNOWLEDGE).read_bytes()):
            result = evaluate_learning(self.current_transfer, self.root, output=self.case / "review", scope_baseline=baseline)
        self.assertEqual(result["status"], SUCCESS, result["findings"])
        self.assertEqual(result["mode"], result["transfer_mode"])

    def test_cp13_repair_invalidates_earlier_cp10_source_receipt(self):
        session = self.case / "earlier_release"
        # The shared suite also runs in completed workspaces. Establish this
        # test's own faulty before-state instead of assuming delivered starters.
        with replaced(self.root / REVIEW, (self.root / "reader_side/learning/unsafe_transfer_review.json").read_bytes()), \
             replaced(self.root / KNOWLEDGE, (self.root / "reader_side/learning/unsafe_team_knowledge.json").read_bytes()):
            rehearsal = rehearse_release(session, root=self.root)
            self.assertEqual(rehearsal["status"], "READY_FOR_DOSSIER_REVIEW", rehearsal["findings"])
            dossier = self.root / "reader_side/reference_solution/ch10/release_dossier.json"
            before = evaluate_release(dossier, session, self.root)
            self.assertEqual(before["status"], "PASS_LOCAL_RELEASE_REHEARSAL_ONLY", before["findings"])
            with replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()), \
                 replaced(self.root / KNOWLEDGE, (self.root / REFERENCE_KNOWLEDGE).read_bytes()):
                after = evaluate_release(dossier, session, self.root)
        self.assertEqual(after["status"], "FAIL")
        for name in (REVIEW, KNOWLEDGE):
            self.assertIn("STALE_INPUT:" + name, after["findings"])

    def test_reference_session_cannot_certify_working_candidates(self):
        result = evaluate_learning(self.transfer, self.root, output=self.case / "review")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("TRANSFER_STATUS_OR_MODE", result["findings"])

    def test_receipt_recheck_and_source_invalidation(self):
        with replaced(self.root / REVIEW, (self.root / REFERENCE_REVIEW).read_bytes()), \
             replaced(self.root / KNOWLEDGE, (self.root / REFERENCE_KNOWLEDGE).read_bytes()):
            first = self.case / "first"
            self.assertEqual(evaluate_learning(self.current_transfer, self.root, output=first)["status"], SUCCESS)
            receipt = first / "LEARNING_RESULT.json"
            self.assertEqual(evaluate_learning(self.current_transfer, self.root, output=self.case / "again", receipt=receipt)["status"], SUCCESS)
            with replaced(self.root / HISTORY, (self.root / HISTORY).read_bytes() + b"\n# stale dependency\n"):
                changed = evaluate_learning(self.current_transfer, self.root, output=self.case / "changed", receipt=receipt)
        self.assertEqual(changed["status"], "FAIL")
        self.assertIn("STALE_TRANSFER_INPUT:" + HISTORY, changed["findings"])
        self.assertIn("policy_activation", changed["affected_knowledge_claims"])
        self.assertIn("state_selection", changed["affected_knowledge_claims"])

    def test_changed_event_evidence_fails_closed(self):
        transfer = self.case / "transfer"
        shutil.copytree(self.transfer, transfer)
        (transfer / "steps/T02_activation.log").write_text("substituted")
        result = evaluate_learning(transfer, self.root, reference=True, output=self.case / "review")
        self.assertIn("STALE_EVIDENCE:steps/T02_activation.log", result["findings"])

    def test_cp13_does_not_allow_cp12_configuration_edit(self):
        baseline = self.case / "baseline.json"
        write_json(baseline, capture_edit_scope("CP13", self.root))
        path = self.root / "repo/engineering/operations/deployment.json"
        with replaced(path, path.read_bytes() + b"\n"):
            result = evaluate_learning(self.transfer, self.root, reference=True, output=self.case / "review", scope_baseline=baseline)
        self.assertIn("OUT_OF_SCOPE:engineering/operations/deployment.json", result["findings"])

    def test_early_delay_and_transfer_release_refused_without_artifact_changes(self):
        self.start()
        self.answer("baseline")
        before = tree_hashes(self.trial)
        with self.assertRaisesRegex(ValueError, "DELAY_NOT_ELAPSED"):
            release_retention(self.owner, self.root, self.clock())
        with self.assertRaisesRegex(ValueError, "RETENTION_MUST_BE_SEALED"):
            release_transfer(self.owner, self.root, self.clock())
        self.assertEqual(tree_hashes(self.trial), before)

    def test_retention_is_sealed_before_only_fault_material_is_published(self):
        self.start()
        self.answer("baseline")
        release_retention(self.owner, self.root, self.clock(86400))
        with self.assertRaisesRegex(ValueError, "RETENTION_MUST_BE_SEALED"):
            release_transfer(self.owner, self.root, self.clock())
        self.answer("retention")
        preserved = digest(self.trial / "answers/retention.raw.md")
        release_transfer(self.owner, self.root, self.clock())
        self.assertEqual(digest(self.trial / "answers/retention.raw.md"), preserved)
        self.assertTrue((self.trial / "transfer_material/T02_activation.json").is_file())
        self.assertFalse(list((self.trial / "transfer_material").glob("U*")))
        self.assertFalse((self.trial / "team_knowledge.json").exists())
        self.answer("transfer")
        self.assertTrue((self.trial / "team_knowledge.json").is_file())

    def test_human_mode_rejects_clock_injection_before_creation(self):
        with self.assertRaisesRegex(ValueError, "CLOCK_INJECTION_FORBIDDEN"):
            start_trial(self.transfer, self.owner, self.trial, "test_person", ["test_a", "test_b"], "test_c", True,
                        self.root, synthetic=False, clock=self.clock())
        self.assertFalse(self.owner.exists())

    @unittest.skipUnless(platform.system() == "Linux" and Path("/proc/sys/kernel/random/boot_id").is_file(),
                         "Real owner clock requires Linux with a kernel boot ID; synthetic checks remain portable")
    def test_actual_owner_clock_reports_real_host_samples_without_human_claim(self):
        first, second = owner_clock(), owner_clock()
        self.assertEqual(first["kind"], "OWNER_HOST_CLOCK")
        self.assertEqual(first["host_boot"], second["host_boot"])
        self.assertGreaterEqual(second["monotonic_ns"], first["monotonic_ns"])

    def test_owner_clock_rejects_unsupported_hosts_and_missing_boot_identity(self):
        for system in ("Darwin", "Windows"):
            with self.subTest(system=system), patch("learning_pilot_core.platform.system", return_value=system):
                with self.assertRaisesRegex(ValueError, "REAL_CLOCK_REQUIRES_SUPPORTED_LINUX_HOST_BOOT"):
                    owner_clock()
        with patch("learning_pilot_core.platform.system", return_value="Linux"), patch.object(Path, "is_file", return_value=False):
            with self.assertRaisesRegex(ValueError, "REAL_CLOCK_REQUIRES_SUPPORTED_LINUX_HOST_BOOT"):
                owner_clock()

    def test_clock_rollback_jump_and_host_change_fail_closed(self):
        first = self.clock()
        cases = [{**first, "wall_ns": first["wall_ns"] - 1},
                 {**first, "wall_ns": first["wall_ns"] + 500_000_000_000},
                 {**first, "host_boot": "OTHER_SYNTHETIC_HOST"}]
        for sample in cases:
            with self.assertRaises(ValueError):
                checked_clock(SYNTHETIC, sample, first, self.root)

    def test_cli_has_no_backdated_timestamp_argument(self):
        run = subprocess.run([sys.executable, "-B", str(self.root / "reader_side/tools/learning_pilot.py"),
                              "release-retention", "--owner-state", str(self.case / "absent"), "--now", "2000-01-01"],
                             capture_output=True, text=True, env=environment(), timeout=30)
        self.assertEqual(run.returncode, 2)
        self.assertIn("unrecognized arguments", run.stderr)

    def test_owner_key_cannot_be_nested_in_public_output(self):
        with self.assertRaisesRegex(ValueError, "DIRECTORIES_MUST_BE_SEPARATE"):
            start_trial(self.transfer, self.trial / "private_owner", self.trial, "s", ["a", "b"], "c", True,
                        self.root, synthetic=True, clock=self.clock())
        self.assertFalse(self.trial.exists())

    def test_owner_event_backdating_breaks_signature(self):
        self.start()
        self.answer("baseline")
        last = sorted((self.owner / "events").glob("*.json"))[-1]
        value = read_json(last)
        value["state"]["delay_anchor"]["wall_ns"] -= 100_000_000_000_000
        write_json(last, value)
        with self.assertRaisesRegex(ValueError, "OWNER_EVENT_INTEGRITY"):
            release_retention(self.owner, self.root, self.clock(86400))

    def test_changed_raw_answer_blocks_later_phase(self):
        self.start()
        self.answer("baseline")
        (self.trial / "answers/baseline.raw.md").write_text("changed after sealing")
        with self.assertRaisesRegex(ValueError, "TRIAL_RECORDS_CHANGED"):
            release_retention(self.owner, self.root, self.clock(86400))

    def test_first_reviewer_private_until_second_raw_review_is_sealed(self):
        self.ready_for_reviews()
        a = self.form("synthetic_a", 2)
        first = record_score(self.owner, "synthetic_a", a, self.root, self.clock())
        self.assertNotIn("raw_ratings", first)
        self.assertFalse((self.trial / "reviews").exists())
        self.assertEqual((self.owner / "private/synthetic_a.json").read_bytes(), a.read_bytes())
        b = self.form("synthetic_b", 1)
        second = record_score(self.owner, "synthetic_b", b, self.root, self.clock())
        self.assertEqual(second["phase"], "REVIEWS_RECORDED")
        self.assertTrue(second["disagreements"])
        self.assertEqual((self.trial / "reviews/synthetic_a.raw.json").read_bytes(), a.read_bytes())

    def test_duplicate_and_participant_scores_are_rejected(self):
        self.ready_for_reviews()
        path = self.form("synthetic_a")
        with self.assertRaisesRegex(ValueError, "INDEPENDENT_REVIEWER"):
            record_score(self.owner, "synthetic_learner", path, self.root, self.clock())
        record_score(self.owner, "synthetic_a", path, self.root, self.clock())
        with self.assertRaisesRegex(ValueError, "INDEPENDENT_REVIEWER"):
            record_score(self.owner, "synthetic_a", path, self.root, self.clock())

    def test_score_binds_answer_rubric_and_reviewer_identity(self):
        self.ready_for_reviews()
        path = self.form("synthetic_a")
        value = read_json(path)
        value["answer_sha256"]["retention"] = "0" * 64
        write_json(path, value)
        with self.assertRaisesRegex(ValueError, "SCORE_IDENTITY:answer_sha256"):
            record_score(self.owner, "synthetic_a", path, self.root, self.clock())

    def test_rating_range_and_boolean_are_not_valid_scores(self):
        self.ready_for_reviews()
        for invalid in (4, True):
            path = self.form("synthetic_a")
            value = read_json(path)
            value["ratings"]["transfer"]["causal_discrimination"] = invalid
            write_json(path, value)
            with self.assertRaisesRegex(ValueError, "SCORE_DIMENSIONS"):
                record_score(self.owner, "synthetic_a", path, self.root, self.clock())

    def test_synthetic_raters_cannot_be_relabeled_as_human_records(self):
        self.ready_for_reviews()
        for declaration in (True, 0):
            path = self.form("synthetic_a")
            value = read_json(path)
            value["attestations"] = {key: declaration for key in value["attestations"]}
            write_json(path, value)
            with self.assertRaisesRegex(ValueError, "ATTESTATION_MISMATCH"):
                record_score(self.owner, "synthetic_a", path, self.root, self.clock())

    def test_no_adjudication_before_two_raw_reviews(self):
        self.ready_for_reviews()
        path = self.form("synthetic_a")
        with self.assertRaisesRegex(ValueError, "TWO_RAW_REVIEWS_REQUIRED"):
            adjudicate(self.owner, path, self.root, self.clock())

    def test_protected_rubric_change_invalidates_trial(self):
        self.start()
        rubric = self.root / "reader_side/learning/rubric.json"
        with replaced(rubric, rubric.read_bytes() + b"\n"):
            with self.assertRaisesRegex(ValueError, "PILOT_SOURCE_OR_RUBRIC_CHANGED"):
                pilot_status(self.owner, self.root)


if __name__ == "__main__":
    unittest.main()
