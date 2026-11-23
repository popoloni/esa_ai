#!/usr/bin/env python3
"""Check a learner copy and retain a receipt; never grants human acceptance.

Only uses the standard library. Protected inputs are compared with the pinned
source before and after running the unchanged tests. This is an integrity check,
not a sandbox or a replacement for reviewing the candidate.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

BASE_COMMIT = "13a1182fc64c2a2c3b3677852b9dfdd95d4be908"
SOURCE = Path(__file__).resolve().parents[2] / "base_13a1182" / "greenfield_studio"
SELECTORS = {
    "first": "test_first_reservation_confirms",
    "overlap": "test_overlap_fails_without_insert",
    "adjacent": "test_adjacent_reservation_succeeds",
    "assets": "test_different_assets_do_not_conflict",
    "replay": "test_same_request_key_replays_original",
    "changed-key": "test_changed_request_with_same_key_fails",
    "invalid-interval": "test_invalid_zero_or_reverse_interval_has_no_effect",
    "duration-format": "test_duration_limit_and_timestamp_format",
    "member-scope": "test_other_member_same_key_is_independent_but_conflicts_on_slot",
    "concurrent": "test_two_writers_do_not_both_confirm_same_slot",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def protected_state(candidate):
    rows = []
    for folder in ("docs", "tests"):
        for source in sorted((SOURCE / folder).rglob("*")):
            if source.is_file():
                rel = source.relative_to(SOURCE)
                target = candidate / rel
                rows.append({"path": str(rel), "expected_sha256": digest(source),
                             "candidate_sha256": digest(target),
                             "symlink": target.is_symlink()})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new receipt path")
    parser.add_argument("--select", choices=["all", *SELECTORS], default="all")
    parser.add_argument("--timeout-seconds", type=float, default=60,
                        help="stop a stalled check and retain its receipt (default: 60)")
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        parser.error("timeout must be greater than zero")
    candidate = args.candidate.expanduser().resolve()
    output = args.output.expanduser().absolute()
    if output.exists():
        parser.error("receipt already exists; choose a new path to preserve the attempt")
    if output.resolve().is_relative_to(SOURCE.parent):
        parser.error("store receipts outside the unchanged base snapshot")
    if not SOURCE.is_dir():
        parser.error("the pinned base_13a1182 snapshot must accompany this tool")
    entry_path = candidate / "READER_ENTRY.json"
    try:
        entry = json.loads(entry_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        parser.error("candidate must be a scaffolded copy with READER_ENTRY.json")
    if entry.get("route") != "GREENFIELD_RESERVATION_STUDIO":
        parser.error("this tool accepts only the Greenfield Reservation learner route")
    if entry.get("mode") == "REFERENCE":
        parser.error("a reference copy is not a learner candidate; use check_reference.py separately")
    before = protected_state(candidate)
    changed = [r["path"] for r in before if r["symlink"] or r["expected_sha256"] != r["candidate_sha256"]]
    candidate_file = candidate / "booking.py"
    candidate_before = digest(candidate_file)
    report = {"schema": "esa-gf-check-receipt/v1", "base_commit": BASE_COMMIT,
              "candidate_path": str(candidate), "candidate_sha256_before": candidate_before,
              "selection": args.select, "protected_before": before,
              "status": "NOT_RUN", "human_acceptance": "PENDING",
              "meaning": "Selected checks on the identified learner candidate; not production authorization, measured learning or autonomous success. Integrity checks do not enforce a sandbox."}
    if changed or candidate_before is None or candidate_file.is_symlink():
        report.update(status="INPUT_INTEGRITY_FAILED", protected_changes=changed,
                      candidate_missing_or_symlink=candidate_before is None or candidate_file.is_symlink())
        code = 2
    else:
        command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
        if args.select != "all":
            command.extend(["-k", SELECTORS[args.select]])
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        start = time.monotonic()
        timed_out = False
        try:
            run = subprocess.run(command, cwd=candidate, env=env, text=True,
                                 capture_output=True, timeout=args.timeout_seconds)
            stdout, stderr, returncode = run.stdout, run.stderr, run.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            # TimeoutExpired may retain bytes even when text=True was requested.
            def decoded(value):
                return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else (value or "")
            stdout, stderr, returncode = decoded(exc.stdout), decoded(exc.stderr), None
        duration = time.monotonic() - start
        after = protected_state(candidate)
        output_text = stdout + stderr
        match = re.search(r"Ran (\d+) tests?", output_text)
        count = int(match.group(1)) if match else 0
        expected_count = 10 if args.select == "all" else 1
        candidate_after = digest(candidate_file)
        inputs_unchanged = before == after and candidate_before == candidate_after
        passed = not timed_out and returncode == 0 and count == expected_count and inputs_unchanged
        report.update(command=command, interpreter=sys.version, elapsed_process_seconds=duration,
                      tests_run=count, expected_tests=expected_count, returncode=returncode,
                      timeout_seconds=args.timeout_seconds, timed_out=timed_out,
                      stdout=stdout, stderr=stderr, protected_after=after,
                      candidate_sha256_after=candidate_after, inputs_unchanged=inputs_unchanged,
                      status="SELECTED_CHECKS_PASSED" if passed else "CHECKS_FAILED")
        code = 0 if passed else 1
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation preserves an earlier receipt if another process won the race.
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "receipt": str(output),
                      "selection": args.select, "tests_run": report.get("tests_run", 0)}, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
