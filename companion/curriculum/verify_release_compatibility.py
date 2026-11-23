#!/usr/bin/env python3
"""Exercise previously issued learner directories against a selected companion.

Recorded entry bytes, learner files and protected inputs are restored by digest.
This is an offline author control. The model launcher is never invoked.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
FIXTURES = HERE / "issued_entries"
LEGACY = ("ESA-Complete-Review-3-20261103", "ESA-Agent-Process-Review-4-20261116",
          "Engineering-Software-with-Agentic-AI-Review-5.2-20261117")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def inventory(path):
    return {p.relative_to(path).as_posix(): sha(p.read_bytes())
            for p in sorted(path.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def restore(snapshot, destination):
    for name, row in snapshot["files"].items():
        data = ((SOURCE / row["companion_source"]).read_bytes() if "companion_source" in row
                else row["utf8"].encode("utf-8"))
        require(sha(data) == row["sha256"], f"Historical fixture bytes changed: {name}")
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def verify(target, output):
    output.mkdir(parents=True, exist_ok=False)
    rows, issued = [], []
    evidence = output / "receipts"
    evidence.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)

    def run(label, arguments, status=None, expected=0, message=None, program="start.py"):
        command = [sys.executable, str(target / program), *map(str, arguments)]
        proc = subprocess.run(command, text=True, capture_output=True, timeout=90, env=env)
        rows.append({"label": label, "command": command, "expected_returncode": expected,
                     "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
        require(proc.returncode == expected, f"{label}: expected {expected}, got {proc.returncode}: {proc.stderr}")
        if message:
            require(message in proc.stderr, f"{label}: missing expected refusal: {proc.stderr}")
        if status:
            require(json.loads(proc.stdout)["status"] == status, f"{label}: {proc.stdout}")
        return proc

    def check(label, operation, mission, candidate, expected_status):
        path = evidence / (label + ".json")
        run(label, [operation, mission, "--candidate", candidate, "--output", path], expected_status)
        receipt = json.loads(path.read_text())
        require(receipt["tests_run"] > 0, f"{label}: zero methods")
        if operation == "continue":
            require(receipt["candidate_retained"], f"{label}: candidate changed during handoff")
        return receipt

    error = None
    try:
        active = json.loads(run("target_identity", ["doctor"], "READY").stdout)["release"]
        for fixture in sorted(FIXTURES.glob("*.json")):
            package = json.loads(fixture.read_text())
            release = package["release"]
            require(release not in issued, f"Duplicate source release: {release}")
            issued.append(release)
            folder = output / fixture.stem
            for mission, snapshot in package["candidates"].items():
                candidate = folder / mission
                restore(snapshot, candidate)
                entry = json.loads((candidate / "READER_ENTRY.json").read_text())
                require(entry["release"] == release and entry["mission"] == mission and
                        entry["mode"] != "REFERENCE", f"{fixture.name}: wrong issued identity")
                before = inventory(candidate)
                label = fixture.stem + "-" + mission
                check(label + "-check", "check", mission, candidate, "SELECTED_CHECKS_PASSED")
                handoff = "SCOPED_HANDOFF_READY" if mission == "G1" else "CONTEXT_HANDOFF_READY"
                check(label + "-continue", "continue", mission, candidate, handoff)
                session = folder / (mission + "-session")
                run(label + "-session", ["prepare", mission, "--candidate", candidate, "--output", session],
                    program="agent_session.py")
                require(json.loads((session / "SESSION.json").read_text())["entry"] == entry,
                        f"{label}: session lost entry provenance")
                if mission == "B1":
                    extension = folder / "B1-v2"
                    run(label + "-extend", ["extend", "B1", "--candidate", candidate, "--dest", extension],
                        "V2_WORKING_COPY_CREATED")
                    version_two = json.loads((extension / "READER_ENTRY.json").read_text())
                    require(version_two["release"] == release and version_two["api_contract"] == "B1-API/v2"
                            and version_two["parent_candidate_sha256"] == before["src/treasury/routing.py"],
                            f"{label}: extension lost its parent")
                    require(version_two.get("extended_by_release") == active,
                            f"{label}: missing or incorrect extension release")
                    shutil.copyfile(target / "solutions/B1/routing_v2.py", extension / "src/treasury/routing.py")
                    check(label + "-v2-handoff", "continue", "B1", extension, "CONTEXT_HANDOFF_READY")
                require(inventory(candidate) == before, f"{label}: original candidate changed")
            require(set(package["candidates"]) == {"G1", "B1"}, f"{release}: both routes required")
        require(active in issued, f"Capture both learner entries under the issuing release {active}")
        # Exercise the same metadata boundary through actual public commands. These
        # cases are deliberately constructed, unlike the authentic snapshots above.
        sample = json.loads(next(iter(sorted(FIXTURES.glob("*.json")))).read_text())["candidates"]["B1"]
        for index, identity in enumerate((*LEGACY, "unissued", active + "-future", None)):
            candidate = output / ("identity-" + str(index))
            restore(sample, candidate)
            path = candidate / "READER_ENTRY.json"
            entry = json.loads(path.read_text())
            entry["release"] = identity
            path.write_text(json.dumps(entry))
            args = ["check", "B1", "--candidate", candidate, "--output", evidence / f"identity-{index}.json"]
            if identity in LEGACY:
                run(f"retained-identity-{index}", args, "SELECTED_CHECKS_PASSED")
            else:
                run(f"unknown-identity-{index}", args, expected=2, message="different mission or release")
                run(f"unknown-session-{index}", ["prepare", "B1", "--candidate", candidate,
                    "--output", output / f"refused-session-{index}"], expected=2,
                    message="different mission or release", program="agent_session.py")
        candidate = output / "identity-0"
        run("wrong-mission", ["continue", "G1", "--candidate", candidate,
            "--output", evidence / "wrong.json"], expected=2, message="different mission or release")
        protected = candidate / "docs/BR-001.md"
        protected.write_bytes(protected.read_bytes() + b"\nChanged by the negative control.\n")
        receipt = evidence / "changed.json"
        run("changed-protected-input", ["check", "B1", "--candidate", candidate, "--output", receipt],
            "INPUT_INTEGRITY_FAILED", expected=1)
        require(json.loads(receipt.read_text())["tests_run"] == 0, "Changed inputs reached the tests")
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        error = str(exc)
    report = {"status": "FAIL" if error else "PASS", "error": error, "observed_model_runs": 0,
              "observed_human_readers": 0, "issued_releases_tested": issued,
              "commands": rows, "command_count": len(rows)}
    (output / "RESULTS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "error", "command_count")}))
    return error is None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--companion", type=Path, default=SOURCE, help="Runtime to test (default: this companion)")
    parser.add_argument("--output", type=Path, required=True, help="Fresh directory outside the companion")
    args = parser.parse_args()
    raise SystemExit(0 if verify(args.companion.resolve(), args.output.resolve()) else 1)
