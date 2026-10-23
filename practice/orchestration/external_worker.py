#!/usr/bin/env python3
"""Bridge the process-controller contract to an externally dispatched worker.

The controller starts this process. A separate coordinator observes DISPATCH.json,
invokes an actual agent through its supported interface, and writes submission.json
atomically. This bridge makes no model call and cannot authenticate that claim.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time

from orchestrator import Refused, atomic_json, confined, regular

SCHEMA = "treasury-external-worker-submission/v1"
MAX_BYTES = 1024 * 1024
RESERVED = {"request.json", "result.json", "submission.json", "DISPATCH.json", "stdout.txt", "stderr.txt"}


def sha(path):
    return hashlib.sha256(regular(path).read_bytes()).hexdigest()


def checked_file(attempt, entry):
    if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
        raise Refused("Each artifact needs a relative path and SHA-256")
    relative = entry["path"]
    if Path(relative).parts and Path(relative).parts[0] in RESERVED:
        raise Refused("An artifact may not reuse the adapter's request, result, or logs")
    path = regular(confined(attempt, relative))
    if path.stat().st_size > MAX_BYTES:
        raise Refused("External artifact exceeds 1 MiB")
    if not re.fullmatch(r"[a-f0-9]{64}", str(entry.get("sha256", ""))) or sha(path) != entry["sha256"]:
        raise Refused("External artifact hash mismatch")
    return {"path": relative, "sha256": entry["sha256"], "bytes": path.stat().st_size}


def validate_submission(request_path, submission_path, expected_request_sha256=None):
    attempt = request_path.parent
    if expected_request_sha256 is not None and sha(request_path) != expected_request_sha256:
        raise Refused("Dispatched request changed before submission")
    request = json.loads(regular(request_path).read_text())
    submission_path = regular(submission_path)
    if submission_path.stat().st_size > MAX_BYTES:
        raise Refused("External submission exceeds 1 MiB")
    submission = json.loads(submission_path.read_text())
    if submission.get("schema") != SCHEMA:
        raise Refused("Unsupported external-worker submission schema")
    if submission.get("request_sha256") != sha(request_path):
        raise Refused("External response belongs to a different request")
    if submission.get("task_id") != request["task"]["id"] or submission.get("status") != "COMPLETED":
        raise Refused("External response must complete the matching task")
    provenance = submission.get("provenance", {})
    if provenance.get("origin") not in ("external_model_agent", "deterministic_adapter_test"):
        raise Refused("Disclose actual external-model or deterministic-test origin")
    if not isinstance(provenance.get("client"), str) or not provenance["client"].strip():
        raise Refused("Name the actual dispatch interface")
    if "model" not in provenance:
        raise Refused("Record the exposed model identity, or null when unknown")
    if not isinstance(submission.get("summary"), str) or not submission["summary"].strip():
        raise Refused("A substantive completion summary is required")
    artifacts = submission.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise Refused("Retain at least one work artifact")
    checked = [checked_file(attempt, entry) for entry in artifacts]
    raw = checked_file(attempt, submission.get("raw_output"))
    names = [entry["path"] for entry in checked]
    if len(names) != len(set(names)):
        raise Refused("Duplicate artifact path")
    expected = request["task"].get("parameters", {}).get("required_artifacts", [])
    if not isinstance(expected, list) or any(name not in names for name in expected):
        raise Refused("A required task artifact is missing")
    return {
        "task_id": submission["task_id"], "status": "COMPLETED",
        "summary": submission["summary"], "worker_kind": "EXTERNALLY_DISPATCHED",
        "request_sha256": submission["request_sha256"], "submission_sha256": sha(submission_path),
        "provenance": provenance, "artifacts": checked, "raw_output": raw,
        "observed_by_bridge": "Request-bound files received and hashes checked; dispatch identity is separately evidenced by the coordinator.",
        "engineering_acceptance": "PENDING_INDEPENDENT_REVIEW",
        "acceptance_authority": False, "release_authority": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--response", required=True, type=Path)
    args = parser.parse_args()
    request_path, response_path = args.request.absolute(), args.response.absolute()
    try:
        request = json.loads(regular(request_path).read_text())
        attempt = request_path.parent
        if not response_path.is_relative_to(attempt):
            raise Refused("Response must stay within the current attempt")
        response_path = confined(attempt, str(response_path.relative_to(attempt)))
        if response_path.exists():
            raise Refused("Response already exists")
        submission_path = confined(attempt, "submission.json")
        if submission_path.exists():
            raise Refused("Submission predates external dispatch")
        dispatch = {
            "schema": "treasury-external-dispatch/v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "request_path": str(request_path), "request_sha256": sha(request_path),
            "task_id": request["task"]["id"], "input_root": request["input_root"],
            "attempt_output_root": str(attempt), "submission_path": str(submission_path),
            "submission_schema": SCHEMA,
            "instruction": "Dispatch an actual worker with this request; retain its prompt, output, exposed identity and context limits. Write submission.json atomically after all referenced artifacts exist. Do not relabel a fixture as an agent run.",
        }
        atomic_json(confined(attempt, "DISPATCH.json"), dispatch)
        print(json.dumps({"dispatch_ready": True, "task_id": request["task"]["id"]}), flush=True)
        # The enclosing controller enforces the task and whole-run deadlines.
        deadline = time.monotonic() + request["task"]["timeout_seconds"]
        while not submission_path.exists():
            if time.monotonic() >= deadline:
                print("External dispatch received no submission before its deadline", file=sys.stderr)
                return 124
            time.sleep(0.1)
        result = validate_submission(request_path, submission_path, dispatch["request_sha256"])
        atomic_json(response_path, result)
        return 0
    except (Refused, OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(json.dumps({"external_worker_status": "REFUSED", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
