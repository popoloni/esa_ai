"""Adversarial CP10 checks on one disposable real-Git rehearsal per test class.

The fixture prepares earlier chapter candidates only in its private copy. It
does not run the shared test runner recursively or edit delivered candidates.
"""
from pathlib import Path
import copy
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "reader_side/tools"))
import release_core as release
from scope_guard import capture_edit_scope, check_edit_scope


class ReleaseEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="cp10-tests-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name) / "companion"
        for relative in release.source_manifest(ROOT):
            path = cls.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / relative).read_bytes())
        for candidate, reference in release.INPUT_PAIRS.values():
            (cls.root / candidate).write_bytes((cls.root / reference).read_bytes())
        cls.session = Path(cls.temporary.name) / "session"
        cls.rehearsal = release.rehearse(cls.session, root=cls.root)
        if cls.rehearsal.get("status") != "READY_FOR_DOSSIER_REVIEW":
            raise AssertionError(json.dumps(cls.rehearsal, indent=2))
        cls.safe = (cls.root / release.REFERENCE).read_bytes()

    def setUp(self):
        (self.root / release.DOSSIER).write_bytes(self.safe)

    def gate(self, candidate=None, baseline=None):
        return release.evaluate_release(candidate or self.root / release.DOSSIER,
                                        self.session, root=self.root, scope_baseline=baseline)

    def change_file(self, path, data):
        original = path.read_bytes()
        self.addCleanup(path.write_bytes, original)
        path.write_bytes(data)

    def change_dossier(self, **changes):
        dossier = json.loads(self.safe)
        dossier.update(changes)
        (self.root / release.DOSSIER).write_bytes(release.json_bytes(dossier))

    def change_record(self, change):
        record = copy.deepcopy(self.rehearsal)
        change(record)
        self.change_file(self.session / "rehearsal.json", release.json_bytes(record))

    def assertRejected(self, finding, result=None):
        result = result or self.gate()
        self.assertEqual("FAIL", result["status"], result)
        self.assertEqual("NOT_AUTHORIZED", result["local_release_decision"], result)
        self.assertIn(finding, result["findings"], result)
        self.assertFalse(result["real_release_authorized"])
        return result

    def test_correct_dossier_preserves_separate_decisions_and_pending_authority(self):
        result = self.gate()
        self.assertEqual(release.SUCCESS, result["status"], result)
        self.assertEqual("PASS", result["ci_status"])
        self.assertEqual("ACCEPT", result["review_decision"])
        self.assertEqual("AUTHORIZE_LOCAL_PRESENTATION_EXPERIMENT", result["local_release_decision"])
        self.assertEqual("PASS", result["rollback_status"])
        self.assertEqual("PENDING_HUMAN", result["CP07_T07_03"])
        self.assertEqual("BLOCKED", result["CP07_T07_04"])
        self.assertFalse(result["real_human_acceptance"])
        self.assertFalse(result["real_release_authorized"])
        self.assertFalse(result["payment_authorized"])

    def test_protected_faulty_control_survives_learner_dossier_repair(self):
        self.assertEqual(release.SUCCESS, self.gate()["status"])
        result = self.gate(self.root / release.UNSAFE)
        self.assertRejected("SELF_APPROVAL", result)
        self.assertIn("UNRESOLVED_MANDATORY_THREAD:THREAD-10-01", result["findings"])
        self.assertIn("EXPLICIT_LOCAL_RELEASE_AUTHORIZATION_MISSING", result["findings"])

    def test_actual_merge_is_materialized_and_artifact_is_reproducible(self):
        state = self.rehearsal["git"]
        self.assertNotEqual(state["head_commit"], state["merge_commit"])
        self.assertNotEqual(state["base_commit"], state["head_commit"])
        self.assertTrue((self.session / "checked_tree/CP10_TARGET_NOTE.txt").is_file())
        committed = release._tree_files(self.session / "repository", state["merge_commit"])
        self.assertEqual(committed[release.PRODUCER], (self.session / "checked_tree" / release.PRODUCER).read_bytes())
        self.assertEqual((self.session / "artifacts/current.zip").read_bytes(),
                         release._artifact_bytes(self.session / "repository", state["merge_commit"], "current"))

    def test_changed_base_is_blocked_even_when_head_is_unchanged(self):
        repo = self.session / "repository"
        self.addCleanup(release._git, repo, "update-ref", "refs/heads/target", self.rehearsal["git"]["base_commit"])
        release._git(repo, "update-ref", "refs/heads/target", self.rehearsal["git"]["head_commit"])
        self.assertRejected("STALE_BASE")

    def test_changed_head_is_blocked_separately(self):
        repo = self.session / "repository"
        self.addCleanup(release._git, repo, "update-ref", "refs/heads/candidate", self.rehearsal["git"]["head_commit"])
        release._git(repo, "update-ref", "refs/heads/candidate", self.rehearsal["git"]["previous_commit"])
        self.assertRejected("STALE_HEAD")

    def test_working_candidate_change_invalidates_evidence(self):
        path = self.root / release.PRODUCER
        self.change_file(path, path.read_bytes() + b"\n# Changed after CI.\n")
        self.assertRejected("STALE_INPUT:" + release.PRODUCER)

    def test_dirty_git_worktree_cannot_substitute_for_recorded_commit(self):
        path = self.session / "repository" / release.PRODUCER
        self.change_file(path, path.read_bytes() + b"\n# Uncommitted source.\n")
        self.assertRejected("DIRTY_REHEARSAL_WORKTREE")

    def test_checked_merge_tree_change_invalidates_evidence(self):
        path = self.session / "checked_tree" / release.PRODUCER
        self.change_file(path, path.read_bytes() + b"\n# Changed after materialization.\n")
        self.assertRejected("CHECKED_TREE_CHANGED")

    def test_missing_required_ci_check_fails_closed(self):
        self.change_record(lambda record: record["checks"].pop("CI-ROUTING-001"))
        self.assertRejected("MISSING_REQUIRED_CHECKS")

    def test_green_ci_for_different_identity_is_stale(self):
        def change(record):
            record["checks"]["CI-ROUTING-001"]["binding"] = {**record["binding"], "head_commit": record["git"]["previous_commit"]}
        self.change_record(change)
        self.assertRejected("STALE_CHECK:CI-ROUTING-001")

    def test_author_cannot_self_approve_green_ci(self):
        self.change_dossier(review_decision_id="REVIEW-10-SELF")
        self.assertRejected("SELF_APPROVAL")

    def test_dossier_claim_cannot_resolve_mandatory_discussion(self):
        self.change_dossier(discussion_resolution_ids=["RESOLUTION-10-02"], all_threads_resolved=True)
        self.assertRejected("UNRESOLVED_MANDATORY_THREAD:THREAD-10-01")

    def test_explicit_owner_rejection_is_not_overridden_by_green_checks(self):
        self.change_dossier(review_decision_id="REVIEW-10-REJECT")
        result = self.assertRejected("OWNER_REVIEW_REJECTED")
        self.assertEqual("REJECT", result["review_decision"])

    def test_review_acceptance_is_not_release_authorization(self):
        self.change_dossier(release_decision_id="RELEASE-10-DENY")
        result = self.assertRejected("EXPLICIT_LOCAL_RELEASE_AUTHORIZATION_MISSING")
        self.assertEqual("ACCEPT", result["review_decision"])

    def test_missing_release_decision_fails_closed(self):
        self.change_dossier(release_decision_id="unknown-owner-decision")
        self.assertRejected("EXPLICIT_LOCAL_RELEASE_AUTHORIZATION_MISSING")

    def test_candidate_artifact_substitution_is_rejected_before_smoke(self):
        path = self.session / "artifacts/current.zip"
        self.change_file(path, path.read_bytes() + b"substituted")
        self.assertRejected("ARTIFACT_SUBSTITUTION:current")

    def test_previous_artifact_cannot_be_replaced_with_current(self):
        self.change_file(self.session / "artifacts/previous.zip", (self.session / "artifacts/current.zip").read_bytes())
        self.assertRejected("ARTIFACT_SUBSTITUTION:previous")

    def test_dossier_cannot_release_a_different_artifact_id(self):
        self.change_dossier(artifact_id="CP10-PREVIOUS")
        self.assertRejected("DOSSIER_ARTIFACT_SUBSTITUTION")

    def test_dossier_must_name_the_distinct_previous_artifact(self):
        self.change_dossier(rollback_artifact_id="CP10-CURRENT")
        self.assertRejected("DOSSIER_ROLLBACK_ARTIFACT")

    def test_rollback_must_restore_the_actual_current_selection(self):
        previous = self.rehearsal["artifacts"]["previous"]
        self.change_file(self.session / "selected_artifact.json", release.json_bytes(
            {"artifact_id": previous["id"], "sha256": previous["sha256"], "file": previous["file"]}))
        self.assertRejected("ROLLBACK_NOT_RESTORED")

    def test_runtime_owner_record_cannot_invent_an_approval(self):
        def change(record):
            record["owner_records"]["review_decisions"][0]["actor_id"] = "candidate-author"
        self.change_record(change)
        self.assertRejected("OWNER_RECORD_BINDING_MISMATCH")

    def test_production_and_cp07_execution_claims_are_rejected(self):
        claims = json.loads(self.safe)["claims"]
        claims.update(production_deployed=True, cp07_t07_04_executed=True)
        self.change_dossier(claims=claims)
        self.assertRejected("AUTHORITY_OVERCLAIM")

    def test_cp10_actual_scope_rejects_an_earlier_candidate_edit(self):
        path = Path(self.temporary.name) / "scope-baseline.json"
        release.write_json(path, capture_edit_scope("CP10", root=self.root))
        router = self.root / "repo/src/treasury/routing.py"
        self.change_file(router, router.read_bytes() + b"\n# Outside Chapter 10.\n")
        self.assertIn("OUT_OF_SCOPE:src/treasury/routing.py", check_edit_scope(path, root=self.root, chapter="CP10"))
        self.assertRejected("OUT_OF_SCOPE:src/treasury/routing.py", self.gate(baseline=path))

    def test_invalid_json_is_a_structured_failure(self):
        (self.root / release.DOSSIER).write_text("{not-json")
        result = self.gate()
        self.assertEqual("FAIL", result["status"])
        self.assertTrue(any(finding.startswith("GATE_ERROR:") for finding in result["findings"]))

    def test_cli_preserves_an_existing_verdict_file(self):
        output = Path(self.temporary.name) / "existing_verdict.json"
        sentinel = b'{"prior_evidence":"preserve these exact bytes"}\n'
        output.write_bytes(sentinel)
        completed = subprocess.run([sys.executable, "-B", str(self.root / "reader_side/tools/release_gate.py"),
                                    "--rehearsal", str(self.session), "--output", str(output)],
                                   cwd=self.root, env=release._environment(), capture_output=True,
                                   text=True, timeout=30)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertEqual(sentinel, output.read_bytes())
        self.assertEqual("", completed.stdout)
        self.assertIn("already exists", completed.stderr)

    def test_green_different_source_is_outside_the_synthetic_decision(self):
        path = self.root / release.PRODUCER
        self.change_file(path, path.read_bytes() + b"\n# Behavior-preserving but separately identified source.\n")
        other = Path(self.temporary.name) / "unapproved-green-source"
        record = release.rehearse(other, root=self.root)
        self.assertEqual("READY_FOR_DOSSIER_REVIEW", record["status"], record)
        self.change_dossier(candidate_source_sha256=release.digest(path))
        result = release.evaluate_release(self.root / release.DOSSIER, other, root=self.root)
        self.assertRejected("SOURCE_NOT_COVERED_BY_SYNTHETIC_OWNER_DECISION", result)
        self.assertEqual("PASS", result["ci_status"])
        self.assertEqual("NOT_ACCEPTED", result["review_decision"])

    def test_malformed_nested_dossier_records_fail_closed(self):
        for key, value in (("claims", []), ("discussion_resolution_ids", {}),
                           ("review_decision_id", []), ("ci_evidence_ids", None)):
            with self.subTest(field=key):
                self.change_dossier(**{key: value})
                result = self.gate()
                self.assertEqual("FAIL", result["status"], result)
                self.assertEqual("NOT_AUTHORIZED", result["local_release_decision"])


if __name__ == "__main__":
    unittest.main()
