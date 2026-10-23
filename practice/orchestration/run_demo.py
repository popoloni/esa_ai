#!/usr/bin/env python3
"""Run real deterministic worker processes and preserve success/failure evidence."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import time

from orchestrator import output_location

HERE = Path(__file__).resolve().parent
COMPANION = HERE.parents[1]
SOURCES = {"routing.py": "repo/src/treasury/routing.py", "intent.md": "reader_side/intent/INT-001.md",
           "protected_plan.json": "reader_side/reference_solution/delegation_plan.json"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def worker(task_id, mode=None, deps=(), attempts=1, timeout=3, **params):
    return {"id": task_id, "kind": "worker", "depends_on": list(deps), "idempotent": True,
            "max_attempts": attempts, "timeout_seconds": timeout, "response": "result.json",
            "parameters": {"mode": mode or task_id, **params}}


def plan(tasks=None):
    return {"schema": "treasury-orchestrator/v1", "worker_kind": "DETERMINISTIC_PYTHON",
            "max_parallel": 2, "max_wall_seconds": 60, "max_output_bytes": 1048576,
            "adapter_argv": ["{python}", "{worker}", "--request", "{request}", "--response", "{response}"],
            "tasks": tasks or [worker("policy", delay_first_attempt=0.1), worker("routing", delay_first_attempt=0.15),
                               worker("synthesis", deps=("policy", "routing"))]}


def setup_case(root, name, spec):
    case = root / name
    case.mkdir()
    (case / "inputs").mkdir()
    for name, source in SOURCES.items():
        shutil.copyfile(COMPANION / source, case / "inputs" / name)
        (case / "inputs" / name).chmod(0o444)
    write(case / "plan.json", spec)
    return case


def command(case, *extra):
    return [sys.executable, str(HERE / "orchestrator.py"), "--plan", str(case / "plan.json"),
            "--inputs", str(case / "inputs"), "--output", str(case / "run"), *extra]


def invoke(case, label, *extra):
    argv = command(case, *extra)
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(argv, text=True, capture_output=True, timeout=15)
    (case / f"{label}.stdout.txt").write_text(result.stdout)
    (case / f"{label}.stderr.txt").write_text(result.stderr)
    receipt = {"argv": argv, "started_at_utc": started, "returncode": result.returncode,
               "stdout": f"{label}.stdout.txt", "stderr": f"{label}.stderr.txt"}
    write(case / f"{label}.json", receipt)
    return result


def state(case):
    return json.loads((case / "run/state.json").read_text())


def scenario_summary(case, expected):
    data = state(case)
    assert data["run_status"] == expected, (case, data["run_status"], expected)
    return {"run_status": data["run_status"], "peak_parallel": data["peak_parallel"],
            "tasks": {i: {"status": r["status"], "attempts": len(r["attempts"]),
                          "outcomes": [a["outcome"] for a in r["attempts"]]} for i, r in data["tasks"].items()},
            "state": str((case / "run/state.json").relative_to(case.parent))}


def preserved_core():
    return {str(p.relative_to(COMPANION)): sha(p) for folder in ("repo", "reader_side")
            for p in (COMPANION / folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def run(output):
    output = output_location(output)
    output.mkdir(parents=True, exist_ok=False)
    before = preserved_core()
    results = {}

    case = setup_case(output, "01_success", plan())
    assert invoke(case, "execute").returncode == 0
    results[case.name] = scenario_summary(case, "COMPLETED")
    first = state(case)
    assert first["peak_parallel"] == 2
    started = [e["task_id"] for e in first["events"] if e["event"] == "TASK_STARTED"]
    assert started == ["policy", "routing", "synthesis"]
    before_attempts = {i: len(r["attempts"]) for i, r in first["tasks"].items()}
    assert invoke(case, "resume_completed", "--resume").returncode == 0
    assert before_attempts == {i: len(r["attempts"]) for i, r in state(case)["tasks"].items()}
    results[case.name]["completed_resume_added_attempts"] = 0

    spec = plan()
    spec["tasks"] += [{"id": "owner_decision", "kind": "human", "depends_on": ["synthesis"]},
                       worker("proposed_implementation", mode="echo", deps=("owner_decision",))]
    case = setup_case(output, "02_human_blocked", spec)
    assert invoke(case, "execute").returncode == 3
    results[case.name] = scenario_summary(case, "WAITING_HUMAN")
    assert state(case)["tasks"]["proposed_implementation"]["attempts"] == []

    case = setup_case(output, "03_retry", plan([worker("retry", mode="retry_once", attempts=2)]))
    assert invoke(case, "execute").returncode == 0
    results[case.name] = scenario_summary(case, "COMPLETED")
    assert results[case.name]["tasks"]["retry"]["outcomes"] == ["NONZERO_EXIT", "COMPLETED"]

    case = setup_case(output, "04_failed_dependency", plan([worker("failure", mode="fail"), worker("dependent", mode="echo", deps=("failure",))]))
    assert invoke(case, "execute").returncode == 1
    results[case.name] = scenario_summary(case, "FAILED")
    assert state(case)["tasks"]["dependent"]["attempts"] == []

    case = setup_case(output, "05_timeout", plan([worker("slow", mode="sleep", timeout=0.15, attempts=2, seconds=2)]))
    assert invoke(case, "execute").returncode == 1
    results[case.name] = scenario_summary(case, "FAILED")
    assert results[case.name]["tasks"]["slow"]["outcomes"] == ["TIMEOUT", "TIMEOUT"]

    spec = plan([worker("policy", delay_first_attempt=0.05),
                 worker("routing", timeout=20, attempts=2, delay_first_attempt=10),
                 worker("synthesis", deps=("policy", "routing"))])
    case = setup_case(output, "06_interrupt_resume", spec)
    argv = command(case)
    with (case / "interrupted.stdout.txt").open("w") as stdout, (case / "interrupted.stderr.txt").open("w") as stderr:
        proc = subprocess.Popen(argv, stdout=stdout, stderr=stderr)
        until = time.monotonic() + 8
        while time.monotonic() < until:
            if (case / "run/state.json").exists():
                data = state(case)
                if data["tasks"]["policy"]["status"] == "COMPLETED" and data["tasks"]["routing"]["status"] == "RUNNING":
                    break
            if proc.poll() is not None:
                raise AssertionError("Coordinator stopped before the interruption point")
            time.sleep(0.02)
        else:
            proc.kill()
            proc.wait()
            raise AssertionError("Interruption point was not reached")
        proc.send_signal(signal.SIGINT)
        assert proc.wait(timeout=5) == 130
    write(case / "interrupt_receipt.json", {"argv": argv, "signal": "SIGINT", "returncode": 130,
                                            "note": "Actual cooperative signal interruption; not a power-loss or SIGKILL experiment."})
    shutil.copyfile(case / "run/state.json", case / "state_interrupted.json")
    assert invoke(case, "resume_without_authorization", "--resume").returncode == 3
    shutil.copyfile(case / "run/state.json", case / "state_reconciliation_required.json")
    assert invoke(case, "resume_idempotent", "--resume", "--retry-interrupted").returncode == 0
    results[case.name] = scenario_summary(case, "COMPLETED")
    assert results[case.name]["tasks"]["policy"]["attempts"] == 1
    assert results[case.name]["tasks"]["routing"]["outcomes"] == ["INTERRUPTED", "COMPLETED"]

    case = setup_case(output, "07_stale_input", plan([worker("policy")]))
    assert invoke(case, "execute").returncode == 0
    (case / "inputs/intent.md").chmod(0o644)
    with (case / "inputs/intent.md").open("a") as stream:
        stream.write("\nChanged after the run, solely to test invalidation.\n")
    refused = invoke(case, "resume_changed_input", "--resume")
    assert refused.returncode == 2 and "identity changed" in refused.stdout
    results[case.name] = {"outcome": "REFUSED_CHANGED_INPUT", "returncode": 2}

    spec = plan([worker("escape", mode="echo")])
    spec["tasks"][0]["response"] = "../escape.json"
    case = setup_case(output, "08_escaping_output", spec)
    refused = invoke(case, "execute")
    assert refused.returncode == 2 and "Unsafe relative output" in refused.stdout
    assert not (case / "run").exists()
    results[case.name] = {"outcome": "REFUSED_BEFORE_DISPATCH", "returncode": 2}

    after = preserved_core()
    assert before == after, "The original cumulative lab changed during the extension"
    protected = json.loads((COMPANION / SOURCES["protected_plan.json"]).read_text())
    original_states = {t["id"]: t["state"] for t in protected["tasks"]}
    report = {"schema": "treasury-orchestrator-observation/v1", "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "platform": platform.platform(),
              "worker_kind": "DETERMINISTIC_PYTHON", "model_calls": 0, "named_agent_client_runs": 0,
              "scenarios": results, "scenario_count": len(results), "status": "PASS_LOCAL_DETERMINISTIC_SCOPE",
              "source_files": {source: sha(COMPANION / source) for source in SOURCES.values()},
              "preserved_core_files": len(before), "core_unchanged": True,
              "original_cp07": {"T07-03": original_states["T07-03"], "T07-04": original_states["T07-04"]},
              "limitations": ["Workers are deterministic Python, not LLM agents.", "No OS sandbox, hosted client, production release, power-loss recovery or exactly-once guarantee was tested.",
                              "The task is source inspection and report synthesis, with no repository patch or human acceptance.",
                              "Wall time, attempts and process overlap are observations, not proof of a productivity benefit."]}
    write(output / "OBSERVATIONS.json", report)
    print(json.dumps({"status": report["status"], "scenarios": len(results), "report": str(output / "OBSERVATIONS.json")}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="A new directory; existing directories are never overwritten")
    try:
        run(parser.parse_args().output)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "REFUSED", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
