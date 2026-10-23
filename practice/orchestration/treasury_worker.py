#!/usr/bin/env python3
"""Deterministic teaching workers, not LLM agents or independent reviewers."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(request):
    task, attempt = request["task"], request["attempt"]
    params = task.get("parameters", {})
    mode = params.get("mode", task["id"])
    time.sleep(params.get("delay_first_attempt", 0) if attempt == 1 else params.get("delay", 0))
    if mode == "fail" or (mode == "retry_once" and attempt == 1):
        print("Deliberately injected worker failure", file=sys.stderr)
        return None
    if mode == "sleep":
        time.sleep(params.get("seconds", 5))
    inputs = Path(request["input_root"])
    result = {"task_id": task["id"], "status": "COMPLETED", "worker_kind": "DETERMINISTIC_PYTHON",
              "attempt": attempt, "acceptance_authority": False, "release_authority": False}
    if mode == "policy":
        text = (inputs / "intent.md").read_text()
        plan = json.loads((inputs / "protected_plan.json").read_text())
        states = {t["id"]: t["state"] for t in plan["tasks"]}
        result.update(source_sha256=sha(inputs / "intent.md"),
                      findings={"intent_mentions_5000": "5,000" in text or "5000" in text,
                                "original_architecture_decision": states["T07-03"],
                                "original_implementation": states["T07-04"]})
    elif mode == "routing":
        # Execute only the snapshotted teaching module, with its recorded hash.
        spec = importlib.util.spec_from_file_location("treasury_snapshot", inputs / "routing.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        amounts = ["4999.99", "5000.00", "5000.01", "0", "NaN"]
        result.update(source_sha256=sha(inputs / "routing.py"),
                      policy_version=module.POLICY_VERSION,
                      observations=[{"amount": a, "route": module.assess(a).route, "reason": module.assess(a).reason} for a in amounts])
    elif mode == "synthesis":
        dependencies = {}
        for name, evidence in request["dependencies"].items():
            path = Path(evidence["response_path"])
            if sha(path) != evidence["sha256"]:
                raise ValueError("Dependency output changed before consumption")
            dependencies[name] = json.loads(path.read_text())
        result.update(dependency_results=dependencies,
                      conclusion="Observations are ready for a human review. No architecture, payment or release decision is supplied.")
    elif mode == "echo":
        result["message"] = params.get("message", "A worker process actually ran.")
    elif mode == "retry_once":
        result["message"] = "Second attempt completed after the retained injected failure."
    elif mode == "sleep":
        result["message"] = "Sleep completed before timeout."
    else:
        raise ValueError(f"Unknown deterministic worker mode: {mode}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--response", required=True, type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text())
    result = execute(request)
    if result is None:
        return 7
    with args.response.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"task_id": request["task"]["id"], "response_written": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
