#!/usr/bin/env python3
"""Read-only CP1 context tool: call the retained B1 router for three known cases.

The route is a recommendation, never authority to move money. This is a small
CLI example, not an MCP server and not an operating-system sandbox.
"""
import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.candidate.resolve() / "src"))
    routing = importlib.import_module("treasury.routing")
    expected = [
        ("-0.01", "REJECTED", "INVALID_AMOUNT"),
        ("4000.00", "STANDARD_QUEUE", "BELOW_LIMIT"),
        ("5000.00", "HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT"),
    ]
    rows = []
    for amount, route, reason in expected:
        result = asdict(routing.assess(amount))
        if result != {"route": route, "reason": reason, "policy_version": "BR-001/v1"}:
            raise AssertionError(f"Preview disagrees with BR-001/v1 at amount {amount}: {result}")
        rows.append({"amount_eur": amount, "decision": result,
                     "payment_authorized": False})
    print(json.dumps({"status": "PREVIEW_MATCHES_POLICY", "rows": rows,
                      "effect": "Read-only calls; no payment integration exists"}, indent=2))


if __name__ == "__main__":
    main()
