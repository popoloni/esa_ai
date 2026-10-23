#!/usr/bin/env python3
"""Regenerate the explicitly synthetic accounting specimen, never a field run."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import workflow_cost as w


def main():
    root = Path(__file__).resolve().parent / "specimen"
    root.mkdir(exist_ok=True)
    evidence = root / "INVENTED_EVIDENCE.txt"
    evidence.write_text(
        "SYNTHETIC TEACHING CASE. Every time, person, task, charge and decision below is invented.\n"
        "Case: a bounded formatting change prepared, attempted, checked, repaired and reviewed.\n"
        "The first check fails; repair and an independent check overlap for 10 seconds.\n"
        "Human reviewer Alex records 60 seconds of active review and accepts change-1.\n"
        "Fictional complete charges: model USD 0.40, human USD 1.50, infrastructure USD 0.10.\n"
        "The human charge is a fictional receipt, not calculated from the illustrative rate.\n"
        "The later automated acceptance repeats the same logical item; it adds no new outcome.\n"
        "The illustrative USD 90/hour assumption is excluded from observed money fields.\n",
        encoding="utf-8")
    candidate = root / "CANDIDATE.txt"
    candidate.write_text("SYNTHETIC accepted formatting-change artifact.\n", encoding="utf-8")
    account_path = root / "ACCOUNT.json"
    ref = w.fingerprint(evidence, account_path)
    candidate_ref = w.fingerprint(candidate, account_path)
    origin = datetime(2026, 10, 21, 9, tzinfo=timezone.utc)
    def at(seconds):
        return (origin + timedelta(seconds=seconds)).isoformat()
    a = w.new_account("SYNTHETIC-ACCOUNT-001", "Teach interval unions, distinct outcomes and missingness",
                      "Invented teaching interface", "Invented preparation through recorded decision",
                      "SYNTHETIC_TEACHING_CASE", ["No actual people, model calls, invoices or business outcomes"])
    a["boundary"].update(start_utc=at(0), finish_utc=at(250))
    definitions = [
        ("prepare", "preparation", "author", "AGENT", 0, 30, "PASSED"),
        ("attempt-1", "implementation", "author", "AGENT", 30, 90, "PASSED"),
        ("first-check", "verification", "checker", "AUTOMATION", 90, 110, "FAILED"),
        ("repair", "rework", "author", "AGENT", 110, 150, "PASSED"),
        ("overlapping-check", "verification", "checker", "AUTOMATION", 140, 160, "PASSED"),
        ("agent-review", "agent_review", "second-agent", "AGENT", 160, 180, "PASSED"),
        ("human-review", "human_review", "Alex", "HUMAN", 180, 240, "PASSED"),
        ("record", "recording", "author", "AGENT", 240, 250, "PASSED"),
    ]
    for sid, phase, actor, kind, start, end, outcome in definitions:
        a["spans"].append({"id": sid, "phase": phase, "actor": actor, "actor_kind": kind,
                           "measure": "DECLARED_ACTIVE_HUMAN_INTERVAL" if kind == "HUMAN" else "WALL_INTERVAL",
                           "start_utc": at(start), "finish_utc": at(end), "outcome": outcome, "evidence": [ref]})
        a["coverage"][phase] = {"state": "OBSERVED", "reason": "Invented specimen interval", "evidence": [ref]}
    for index, (component, amount) in enumerate((("model", "0.40"), ("human", "1.50"), ("infrastructure", "0.10")), 1):
        a["usage"].append({"id": f"charge-{index}", "kind": "MONEY", "component": component,
                           "value": amount, "unit": "USD", "charge_key": f"INVENTED-INVOICE/{index}",
                           "at_utc": at(249), "evidence": ref})
        a["money_coverage"][component] = {"state": "COMPLETE", "reason": "Invented complete receipt for this specimen", "evidence": [ref]}
    for event_id, kind, when in (("machine-first", "AUTOMATED", 160), ("machine-repeat", "AUTOMATED", 170), ("agent", "AGENT", 180), ("human", "HUMAN", 240)):
        a["acceptance"].append({"id": event_id, "item": "change-1", "kind": kind,
                                "decision": "ACCEPTED", "reviewer": "Alex" if kind == "HUMAN" else kind,
                                "at_utc": at(when), "candidate": candidate_ref, "evidence": ref,
                                "human_attestation": "Invented Alex decision; no human participant exists" if kind == "HUMAN" else None})
    a["assumptions"] = [{"name": "Illustrative alternative hourly rate", "value": "90", "unit": "USD/hour",
                          "basis": "Sensitivity scenario only; never used in the observed-charge arithmetic"}]
    w.validate(a, root)
    w.write_json(account_path, a)
    report = w.summarize(a, root)
    w.write_json(root / "REPORT.json", report)
    print(json.dumps({"status": "CREATED_SYNTHETIC_SPECIMEN", "elapsed_seconds": report["workflow_elapsed_seconds"],
                      "interval_sum": report["sum_of_interval_seconds_not_elapsed"],
                      "union_seconds": report["observed_interval_union_seconds"],
                      "human_accepted_items": report["acceptance"]["HUMAN"]["accepted_distinct_items"],
                      "money": report["complete_workflow_money"], "roi": report["roi"]}))


if __name__ == "__main__":
    main()
