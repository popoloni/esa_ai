#!/usr/bin/env python3
"""Fixed deterministic responder. This is deliberately not an LLM client."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

from common import config_digest, digest, read_json, validate_config


def cached_estimate(amount: str) -> dict:
    """A deliberately inadequate shortcut, retained as the baseline mechanism."""
    try:
        number = float(amount)
        below = number < 5000.0
        route = "STANDARD_QUEUE" if below else "HUMAN_REVIEW"
        reason = "BELOW_LIMIT" if below else "AT_OR_ABOVE_LIMIT"
    except ValueError:
        route, reason = "REJECTED", "INVALID_AMOUNT"
    return {
        "route": route, "reason": reason, "policy_version": "BR-001/v1",
        "payment_authorized": False,
    }


def execute(config: dict, request: dict, router_path: Path) -> dict:
    validate_config(config)
    if set(request) != {"case_id", "amount_eur"}:
        raise ValueError("Worker request must contain only case_id and amount_eur")
    if not all(isinstance(v, str) and len(v) <= 80 for v in request.values()):
        raise ValueError("Worker request fields must be bounded strings")
    amount = request["amount_eur"]
    trace = [{"event": "context", "amount_eur": amount,
              "strategy": config["routing_strategy"], "model_calls": 0}]
    if config["routing_strategy"] == "router_tool":
        spec = importlib.util.spec_from_file_location("treasury_harness_snapshot", router_path)
        if spec is None or spec.loader is None:
            raise ValueError("Cannot load the fixed domain tool")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        observation = asdict(module.assess(amount))
        observation["payment_authorized"] = False
        trace.append({"event": "tool_executed", "tool": "treasury.assess",
                      "input": amount, "observation": observation,
                      "source_sha256": digest(router_path)})
    elif config["routing_strategy"] == "memorized_development" and amount in config["development_memory"]:
        observation = config["development_memory"][amount]
        trace.append({"event": "memory_hit", "input": amount,
                      "note": "Development answer reused; no domain tool executed"})
    else:
        observation = cached_estimate(amount)
        trace.append({"event": "cached_estimate", "input": amount,
                      "note": "Fixed float-based shortcut; no domain tool executed"})
    response = {key: observation[key] for key in config["response_fields"]}
    trace.append({"event": "response_emitted", "fields": sorted(response)})
    return {"schema": "deterministic-harness-execution/v1", "case_id": request["case_id"],
            "response": response, "trace": trace, "config_sha256": config_digest(config),
            "model_calls": 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--router", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = execute(read_json(args.config), json.load(sys.stdin), args.router)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0
    except (ValueError, TypeError, OSError, KeyError) as exc:
        print(json.dumps({"status": "WORKER_ERROR", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

