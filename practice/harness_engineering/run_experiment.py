#!/usr/bin/env python3
"""Run a deterministic Treasury adaptation of Propose/Probe/Compose, without APIs."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import difflib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

from common import (
    COMPANION, REQUIRED_FIELDS, ROOT, config_digest, create_output_directory,
    digest, read_json, require_source_pins, validate_config, validate_tasks, write_json,
)

TIMEOUT_SECONDS = 5
MAX_PROCESS_EXECUTIONS = 80


def base_harness() -> dict:
    return {"schema": "treasury-harness/v1", "routing_strategy": "cached_estimate",
            "response_fields": ["route"], "development_memory": {}}


def execute_process(argv: list[str], request: dict, timeout: float) -> dict:
    started = time.monotonic()
    env = {"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}
    try:
        completed = subprocess.run(argv, input=json.dumps(request), text=True,
                                   capture_output=True, timeout=timeout, env=env,
                                   cwd=ROOT, check=False, shell=False)
        record = {"returncode": completed.returncode, "stdout": completed.stdout,
                  "stderr": completed.stderr, "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        def decode(value):
            return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")
        record = {"returncode": None, "stdout": decode(exc.stdout),
                  "stderr": decode(exc.stderr), "timed_out": True}
    record["elapsed_seconds"] = time.monotonic() - started
    return record


def observe(execution: dict) -> dict:
    """Only task-visible behavior, never oracle scores, reaches the improver."""
    return {
        "case_id": execution["case_id"],
        "fresh_router_calls": sum(e["event"] == "tool_executed" for e in execution["trace"]),
        "required_fields_present": sorted(set(REQUIRED_FIELDS) & set(execution["response"])),
        "response": execution["response"], "trace": execution["trace"],
    }


def compose(candidates: dict, observations: dict) -> tuple[dict, dict]:
    """An authored deterministic editor heuristic, not learned model behavior."""
    ids = list(candidates)
    tool_scores = {name: sum(x["fresh_router_calls"] == 1 for x in observations[name])
                   for name in ids}
    shape_scores = {name: sum(len(x["required_fields_present"]) for x in observations[name])
                    for name in ids}
    tool_source = max(ids, key=tool_scores.get)
    shape_source = max(ids, key=shape_scores.get)
    if tool_scores[tool_source] != len(observations[tool_source]):
        raise ValueError("No proposal demonstrated a domain-tool call for every development input")
    if shape_scores[shape_source] != len(REQUIRED_FIELDS) * len(observations[shape_source]):
        raise ValueError("No proposal demonstrated complete required output fields")
    result = copy.deepcopy(candidates[tool_source])
    result["response_fields"] = copy.deepcopy(candidates[shape_source]["response_fields"])
    result["development_memory"] = {}
    validate_config(result)
    return result, {"tool_scores": tool_scores, "shape_scores": shape_scores,
                    "routing_component_from": tool_source, "response_component_from": shape_source,
                    "selection_uses_oracle_results": False,
                    "reason": "Compose observed fresh domain-tool use with the public output contract; these proxy checks do not establish semantic correctness."}


def suggest_from_library(base: dict, entry: dict, router_sha256: str) -> dict:
    if entry["source_router_sha256"] != router_sha256:
        raise ValueError("STALE_LIBRARY_SOURCE: the retained lesson requires source review")
    if entry["required_fields"] != list(REQUIRED_FIELDS):
        raise ValueError("Library lesson does not match the current output contract")
    result = copy.deepcopy(base)
    result.update(copy.deepcopy(entry["reusable_components"]))
    validate_config(result)
    return result


def score_response(response: dict, expected: dict) -> dict:
    return {"route_correct": response.get("route") == expected["route"],
            "full_contract_correct": response == expected}


def run(output: Path) -> dict:
    pins = require_source_pins()
    protected_before = {rel: digest(COMPANION / rel) for rel in pins["companion_files"]}
    code_before = {p.name: digest(p) for p in [ROOT / "common.py", ROOT / "worker.py", ROOT / "run_experiment.py"]}
    fixture_before = {p.name: digest(p) for p in sorted((ROOT / "fixtures").glob("*.json"))}
    tasks = read_json(ROOT / "fixtures/tasks.json")
    validate_tasks(tasks)
    started = time.monotonic()
    process_count = 0
    tool_calls = 0
    snapshot = output / "source_snapshot"
    snapshot.mkdir()
    router = snapshot / "routing.py"
    shutil.copyfile(COMPANION / "repo/src/treasury/routing.py", router)
    shutil.copyfile(COMPANION / "reader_side/discovery/sources/SRC-POL-001.json", snapshot / "policy.json")
    shutil.copyfile(COMPANION / "reader_side/reference_solution/delegation_plan.json", snapshot / "cp07_reference_plan.json")
    router_hash = digest(router)
    router.chmod(0o444)
    write_json(output / "SOURCE_RECEIPT.json", {"companion_files": protected_before,
               "code_files": code_before, "fixture_files": fixture_before,
               "fixed_router_sha256": router_hash, "source": "current cumulative companion, copied without repair",
               "protection": "Closed configuration schema, before/after identity checks and read-only copy; not an OS sandbox"})
    write_json(output / "TASK_CONTRACT.json", tasks["contract"])
    write_json(output / "RUNTIME_BUDGET.json", {"max_process_executions": MAX_PROCESS_EXECUTIONS,
               "timeout_seconds_per_process": TIMEOUT_SECONDS, "model_calls": 0,
               "candidate_may_edit_budget": False})
    candidates = {"base": base_harness()}
    executions = {}
    observations = {}

    def save_candidate(name: str, config: dict):
        validate_config(config)
        candidates[name] = copy.deepcopy(config)
        path = output / "candidates" / name / "harness.json"
        write_json(path, config)
        a = json.dumps(base_harness(), indent=2, sort_keys=True).splitlines(True)
        b = json.dumps(config, indent=2, sort_keys=True).splitlines(True)
        patch = "".join(difflib.unified_diff(a, b, fromfile="base/harness.json", tofile=f"{name}/harness.json"))
        (path.parent / "change.diff").write_text(patch, encoding="utf-8")

    def probe(name: str, phase: str, selected_tasks: list[dict]):
        nonlocal process_count, tool_calls
        results = []
        for task in selected_tasks:
            if process_count >= MAX_PROCESS_EXECUTIONS:
                raise ValueError("Process execution budget exhausted")
            if digest(router) != router_hash:
                raise ValueError("Fixed domain tool changed during experiment")
            cfg = output / "candidates" / name / "harness.json"
            if read_json(cfg) != candidates[name]:
                raise ValueError("Candidate changed after validation")
            request = {"case_id": task["case_id"], "amount_eur": task["amount_eur"]}
            argv = [sys.executable, str(ROOT / "worker.py"), "--config", str(cfg), "--router", str(router)]
            raw = execute_process(argv, request, TIMEOUT_SECONDS)
            process_count += 1
            receipt = {"candidate": name, "phase": phase, "request": request, "argv": argv,
                       "execution_number": process_count, "raw_process": raw, "validation": "PENDING"}
            receipt_path = output / "probes" / name / phase / (task["case_id"] + ".json")
            # Retain raw process evidence even when an exit-0 worker returns
            # malformed JSON or claims a different request/configuration identity.
            write_json(receipt_path, receipt)
            if raw["timed_out"] or raw["returncode"] != 0:
                receipt["validation"] = "PROCESS_FAILED"
                write_json(receipt_path, receipt)
                raise ValueError(f"Candidate process failed: {name}/{task['case_id']}")
            try:
                result = json.loads(raw["stdout"])
                if result["case_id"] != task["case_id"] or result["config_sha256"] != config_digest(candidates[name]):
                    raise ValueError("Worker result identity does not match the request")
            except (ValueError, KeyError, TypeError) as exc:
                receipt["validation"] = "REJECTED"
                receipt["validation_error"] = str(exc)
                write_json(receipt_path, receipt)
                raise
            receipt["execution"] = result
            receipt["validation"] = "ACCEPTED_FOR_EVALUATION"
            write_json(receipt_path, receipt)
            tool_calls += sum(x["event"] == "tool_executed" for x in result["trace"])
            results.append(result)
        executions.setdefault(name, {})[phase] = results
        return results

    save_candidate("base", base_harness())
    observations["base"] = [observe(x) for x in probe("base", "development", tasks["development"])]
    tool_first = base_harness()
    tool_first["routing_strategy"] = "router_tool"
    save_candidate("tool_first", tool_first)
    observations["tool_first"] = [observe(x) for x in probe("tool_first", "development", tasks["development"])]
    schema_complete = base_harness()
    schema_complete["response_fields"] = list(REQUIRED_FIELDS)
    save_candidate("schema_complete", schema_complete)
    observations["schema_complete"] = [observe(x) for x in probe("schema_complete", "development", tasks["development"])]
    memorized = copy.deepcopy(schema_complete)
    memorized["routing_strategy"] = "memorized_development"
    for result in observations["tool_first"]:
        for event in result["trace"]:
            if event["event"] == "tool_executed":
                memorized["development_memory"][event["input"]] = event["observation"]
    save_candidate("memorized_development", memorized)
    observations["memorized_development"] = [observe(x) for x in probe("memorized_development", "development", tasks["development"])]
    rejected = []
    for name, forbidden in [("policy_rewrite", {"policy_threshold_eur": "3000.00"}),
                             ("budget_rewrite", {"runtime_budget": {"max_process_executions": 1000000}})]:
        proposal = dict(base_harness(), **forbidden)
        try:
            validate_config(proposal)
        except ValueError as exc:
            rejection = {"proposal": proposal, "status": "REJECTED_BEFORE_EXECUTION", "reason": str(exc)}
            write_json(output / "rejected_proposals" / (name + ".json"), rejection)
            rejected.append(name)
        else:
            raise ValueError("A protected-component edit was incorrectly accepted")

    # This is the entire input of the editor/composer. The held-out inputs and
    # the independent oracle are deliberately absent from this data boundary.
    improver_input = {"public_contract": tasks["contract"], "development_tasks": tasks["development"],
                      "candidates": copy.deepcopy(candidates), "observations": observations,
                      "editor_kind": "authored deterministic heuristic", "oracle_scores_available": False}
    write_json(output / "IMPROVER_INPUT.json", improver_input)
    composed, decision = compose(improver_input["candidates"], improver_input["observations"])
    save_candidate("composed", composed)
    write_json(output / "COMPOSITION_DECISION.json", decision)
    probe("composed", "development", tasks["development"])
    entry = {"schema": "harness-improvement-library-entry/v1", "entry_id": "treasury-output-contract-001",
             "source_router_sha256": router_hash, "required_fields": list(REQUIRED_FIELDS),
             "reusable_components": {"routing_strategy": composed["routing_strategy"],
                                     "response_fields": composed["response_fields"], "development_memory": {}},
             "adopted_harness_sha256": config_digest(composed),
             "evidence": ["COMPOSITION_DECISION.json", "IMPROVER_INPUT.json", "probes/composed/development"],
             "lessons": ["Call the domain router for each amount instead of duplicating its arithmetic.",
                         "Emit every field required by the current public task contract."],
             "scope": "A deterministic behavior-guided teaching lesson for the same router and contract; no correctness or transfer guarantee",
             "selection_used_acceptance_scores": False}
    write_json(output / "improvement_library" / "entry_001.json", entry)
    adopted_at = datetime.now(timezone.utc).isoformat()
    write_json(output / "ADOPTION_RECEIPT.json", {"adopted_at_utc": adopted_at,
               "composed_sha256": config_digest(composed), "improver_input_sha256": digest(output / "IMPROVER_INPUT.json"),
               "selection_used_oracle_scores": False, "held_out_has_run": False,
               "note": "Protocol order is an audit record, not an external trusted timestamp"})

    # Evaluation happens only after the harness and reusable lesson are fixed.
    oracle = read_json(ROOT / "fixtures/evaluation_oracle.json")
    evaluated_candidates = list(candidates)
    scores = {}
    for name in evaluated_candidates:
        probe(name, "held_out", tasks["held_out"])
        by_phase = {}
        for phase in ("development", "held_out"):
            rows = [{"case_id": x["case_id"], "response": x["response"],
                     **score_response(x["response"], oracle[x["case_id"]])}
                    for x in executions[name][phase]]
            write_json(output / "evaluation" / name / (phase + ".json"), {"rows": rows,
                       "oracle_sha256": digest(ROOT / "fixtures/evaluation_oracle.json"),
                       "visible_to_improver": False})
            by_phase[phase] = {"cases": len(rows), "route_correct": sum(x["route_correct"] for x in rows),
                               "full_contract_correct": sum(x["full_contract_correct"] for x in rows)}
        scores[name] = by_phase

    # A later task asks for the same kind of response for new amounts. The
    # library proposes components against a fresh base rather than silently
    # copying all task-specific memory from the previous harness.
    reused = suggest_from_library(base_harness(), entry, router_hash)
    save_candidate("library_reuse", reused)
    transfer = probe("library_reuse", "later_tasks", tasks["later_tasks"])
    transfer_rows = [{"case_id": x["case_id"], "response": x["response"],
                     **score_response(x["response"], oracle[x["case_id"]])} for x in transfer]
    write_json(output / "evaluation/library_reuse/later_tasks.json", {"rows": transfer_rows,
               "visible_to_improver": False, "oracle_sha256": digest(ROOT / "fixtures/evaluation_oracle.json")})
    try:
        suggest_from_library(base_harness(), entry, "0" * 64)
    except ValueError as exc:
        stale = {"status": "REJECTED_STALE_REUSE", "reason": str(exc)}
        write_json(output / "improvement_library/rejected_stale_reuse.json", stale)
    else:
        raise ValueError("Stale lesson incorrectly reused")

    protected_after = {rel: digest(COMPANION / rel) for rel in pins["companion_files"]}
    code_after = {name: digest(ROOT / name) for name in code_before}
    fixture_after = {name: digest(ROOT / "fixtures" / name) for name in fixture_before}
    unchanged = protected_before == protected_after and code_before == code_after and fixture_before == fixture_after and digest(router) == router_hash
    if not unchanged:
        raise ValueError("Protected source, runtime, fixture or oracle changed")
    report = {"schema": "treasury-harness-experiment/v1", "status": "COMPLETE_DETERMINISTIC_EXERCISE",
              "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "experiment_kind": "original deterministic behavior-guided adaptation; not an upstream Harness2 reproduction or LLM benchmark",
              "runtime": {"python": platform.python_version(), "platform": platform.platform()},
              "model_calls": 0, "model_version": None, "tokens": None, "model_api_cost": None,
              "human_effort_minutes": None, "statistical_replications": 0,
              "process_executions": process_count, "domain_tool_calls": tool_calls,
              "elapsed_seconds": time.monotonic() - started,
              "scores": scores, "rejected_proposals": rejected,
              "composition": decision,
              "library_reuse": {"later_cases": len(transfer_rows),
                                "full_contract_correct": sum(x["full_contract_correct"] for x in transfer_rows),
                                "stale_source_control": stale["status"]},
              "protection": {"all_selected_sources_runtime_and_oracle_unchanged": unchanged,
                             "before": protected_before, "after": protected_after,
                             "cp07_decision": "T07-03 remains pending; T07-04 remains blocked",
                             "held_out_and_oracle_results_exposed_to_composer": False,
                             "os_sandbox_demonstrated": False},
              "interpretation": "The executable harness changes the behavior of a fixed deterministic responder. Passing fixture cases does not establish an LLM gain, human acceptance, generalization, deployment readiness or production safety."}
    write_json(output / "REPORT.json", report)
    write_json(output / "OUTPUT_SHA256.json", {str(p.relative_to(output)): digest(p)
               for p in sorted(output.rglob("*")) if p.is_file() and p.name != "OUTPUT_SHA256.json"})
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="A new directory; existing paths are refused")
    args = parser.parse_args()
    output = None
    try:
        require_source_pins()
        output = create_output_directory(args.output)
        report = run(output)
        print(json.dumps({"status": report["status"], "report": str(output / "REPORT.json"),
                          "process_executions": report["process_executions"], "model_calls": 0}, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        if output is not None:
            write_json(output / "FAILED.json", {"status": "FAILED", "error": str(exc),
                       "note": "Partial evidence retained; choose a new output directory after correction"})
        print(json.dumps({"status": "FAILED", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
