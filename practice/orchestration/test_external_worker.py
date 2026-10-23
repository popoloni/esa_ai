"""Boundary checks for the file bridge; these tests make zero model calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from external_worker import Refused, SCHEMA, validate_submission


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ExternalWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.attempt = self.root / "attempt"
        self.attempt.mkdir()
        self.request = self.attempt / "request.json"
        self.request.write_text(json.dumps({
            "schema": "treasury-worker-request/v1", "input_root": str(self.root / "inputs"),
            "task": {"id": "spec", "timeout_seconds": 3,
                     "parameters": {"required_artifacts": ["artifacts/spec.md"]}},
        }))
        (self.attempt / "artifacts").mkdir()
        (self.attempt / "artifacts/spec.md").write_text("Deterministic adapter-test artifact.\n")
        (self.attempt / "RAW_RESPONSE.md").write_text("Deterministic adapter test; no model call.\n")
        self.submission = {
            "schema": SCHEMA, "task_id": "spec", "status": "COMPLETED",
            "request_sha256": sha(self.request), "summary": "Exercise a file handoff only.",
            "provenance": {"origin": "deterministic_adapter_test", "client": "Python unittest", "model": None},
            "artifacts": [{"path": "artifacts/spec.md", "sha256": sha(self.attempt / "artifacts/spec.md")}],
            "raw_output": {"path": "RAW_RESPONSE.md", "sha256": sha(self.attempt / "RAW_RESPONSE.md")},
        }
        self.path = self.attempt / "submission.json"

    def tearDown(self):
        self.temporary.cleanup()

    def validate(self):
        self.path.write_text(json.dumps(self.submission))
        return validate_submission(self.request, self.path)

    def test_valid_handoff_preserves_test_origin_and_no_authority(self):
        result = self.validate()
        self.assertEqual(result["provenance"]["origin"], "deterministic_adapter_test")
        self.assertFalse(result["acceptance_authority"])
        self.assertEqual(result["engineering_acceptance"], "PENDING_INDEPENDENT_REVIEW")

    def test_wrong_request_binding_is_rejected(self):
        self.submission["request_sha256"] = "0" * 64
        with self.assertRaisesRegex(Refused, "different request"):
            self.validate()

    def test_request_mutation_after_dispatch_is_rejected(self):
        dispatched_hash = sha(self.request)
        self.request.write_text(self.request.read_text() + "\n")
        self.path.write_text(json.dumps(self.submission))
        with self.assertRaisesRegex(Refused, "request changed"):
            validate_submission(self.request, self.path, dispatched_hash)

    def test_changed_artifact_is_rejected(self):
        (self.attempt / "artifacts/spec.md").write_text("Changed after submission.\n")
        with self.assertRaisesRegex(Refused, "hash mismatch"):
            self.validate()

    def test_path_escape_is_rejected(self):
        outside = self.root / "outside.md"
        outside.write_text("Outside the attempt.\n")
        self.submission["raw_output"] = {"path": "../outside.md", "sha256": sha(outside)}
        with self.assertRaisesRegex(Refused, "Unsafe relative"):
            self.validate()

    def test_symlink_ancestor_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "raw.md").write_text("A symlink must not redirect this read.\n")
        (self.attempt / "redirect").symlink_to(outside, target_is_directory=True)
        self.submission["raw_output"] = {"path": "redirect/raw.md", "sha256": sha(outside / "raw.md")}
        with self.assertRaisesRegex(Refused, "Symlink"):
            self.validate()

    def test_missing_required_artifact_is_rejected(self):
        self.submission["artifacts"] = [self.submission["raw_output"]]
        with self.assertRaisesRegex(Refused, "required task artifact"):
            self.validate()

    def test_process_waits_for_request_bound_submission(self):
        process = subprocess.Popen([sys.executable, str(Path(__file__).with_name("external_worker.py")),
                                    "--request", str(self.request), "--response", str(self.attempt / "result.json")],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 2
            while not (self.attempt / "DISPATCH.json").exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            dispatch = json.loads((self.attempt / "DISPATCH.json").read_text())
            self.assertEqual(dispatch["request_sha256"], self.submission["request_sha256"])
            temporary = self.attempt / "submission.pending"
            temporary.write_text(json.dumps(self.submission))
            temporary.rename(self.path)
            stdout, stderr = process.communicate(timeout=3)
            self.assertEqual(process.returncode, 0, stderr)
            result = json.loads((self.attempt / "result.json").read_text())
            self.assertEqual(result["provenance"]["origin"], "deterministic_adapter_test")
            self.assertIn('"dispatch_ready": true', stdout)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()


if __name__ == "__main__":
    unittest.main()
