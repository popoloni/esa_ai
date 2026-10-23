#!/usr/bin/env python3
"""Prospective, attributable single-workflow accounting. Python standard library only.

This records observations; it does not authenticate people, enforce isolation,
measure provider usage automatically, or infer business value from elapsed time.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

SCHEMA = "esa-workflow-cost/v1"
PHASES = ("preparation", "implementation", "verification", "agent_review",
          "human_review", "rework", "recording")
ACTORS = ("AGENT", "AUTOMATION", "HUMAN")
OUTCOMES = ("PASSED", "FAILED", "ABANDONED", "OBSERVED")
KINDS = ("AUTOMATED", "AGENT", "HUMAN")
MONEY_COMPONENTS = ("model", "human", "infrastructure")
CLAIM_SCOPE = "DESCRIPTIVE_SINGLE_WORKFLOW_NO_CAUSAL_OR_ROI_CLAIM"


class AccountError(ValueError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError) as exc:
        raise AccountError(f"Invalid timestamp: {value!r}") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise AccountError("Timestamps must include a timezone")
    return result.astimezone(timezone.utc)


def number(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise AccountError(f"Invalid numeric value: {value!r}") from exc
    if not result.is_finite() or result < 0:
        raise AccountError("Amounts must be finite and nonnegative")
    return result


def fingerprint(path, account_path):
    path = Path(path).resolve()
    if not path.is_file():
        raise AccountError(f"Evidence is not a regular file: {path}")
    return {"path": os.path.relpath(path, Path(account_path).resolve().parent),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def check_ref(ref, base):
    if not isinstance(ref, dict) or not ref.get("path") or len(ref.get("sha256", "")) != 64:
        raise AccountError("Every evidence reference needs a path and SHA-256")
    if base is not None:
        p = Path(base) / ref["path"]
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != ref["sha256"]:
            raise AccountError(f"Missing or changed evidence: {ref['path']}")


def new_account(run_id, purpose, interface, boundary, mode="OBSERVED", exclusions=()):
    if mode not in ("OBSERVED", "SYNTHETIC_TEACHING_CASE"):
        raise AccountError("Unknown evidence mode")
    return {
        "schema": SCHEMA, "run_id": run_id, "purpose": purpose,
        "evidence_mode": mode, "claim_scope": CLAIM_SCOPE,
        "identity": {"interface": interface, "client_version": "UNKNOWN_NOT_EXPOSED",
                     "model": "UNKNOWN_NOT_EXPOSED", "model_version": "UNKNOWN_NOT_EXPOSED"},
        "boundary": {"description": boundary, "start_utc": utc_now(),
                     "finish_utc": None, "exclusions": list(exclusions)},
        "spans": [], "usage": [], "acceptance": [], "assumptions": [],
        "coverage": {p: {"state": "UNKNOWN", "reason": "Not yet recorded", "evidence": []}
                     for p in PHASES},
        "money_coverage": {p: {"state": "UNKNOWN", "reason": "No complete attributable record",
                               "evidence": []} for p in MONEY_COMPONENTS},
    }


def unique(records, label):
    values = [r.get("id") for r in records]
    if any(not v for v in values) or len(values) != len(set(values)):
        raise AccountError(f"Missing or duplicate {label} id")


def validate(account, base=None):
    if account.get("schema") != SCHEMA or account.get("claim_scope") != CLAIM_SCOPE:
        raise AccountError("Unsupported schema or claim scope")
    if account.get("evidence_mode") not in ("OBSERVED", "SYNTHETIC_TEACHING_CASE"):
        raise AccountError("Unknown evidence mode")
    if any(k in account for k in ("roi", "speedup", "empirical_roi", "business_benefit")):
        raise AccountError("This account does not establish ROI, speedup or business benefit")
    for key in ("run_id", "purpose"):
        if not isinstance(account.get(key), str) or not account[key].strip():
            raise AccountError(f"Missing {key}")
    if not account.get("identity", {}).get("interface"):
        raise AccountError("Missing interface identity")
    b = account["boundary"]
    start = timestamp(b["start_utc"])
    finish = timestamp(b["finish_utc"]) if b["finish_utc"] else None
    if finish and finish < start:
        raise AccountError("Workflow ends before it starts")
    for group in ("spans", "usage", "acceptance"):
        unique(account[group], group)
    actor_kinds = {}
    for span in account["spans"]:
        if span.get("phase") not in PHASES or span.get("actor_kind") not in ACTORS:
            raise AccountError("Unknown phase or actor kind")
        if not span.get("actor"):
            raise AccountError("Missing actor identity")
        old = actor_kinds.setdefault(span["actor"], span["actor_kind"])
        if old != span["actor_kind"]:
            raise AccountError("One actor identity cannot change kind inside this account")
        if span["phase"] == "human_review" and span["actor_kind"] != "HUMAN":
            raise AccountError("An agent or automation interval cannot be human review")
        if span["phase"] == "agent_review" and span["actor_kind"] != "AGENT":
            raise AccountError("Agent review needs an agent actor")
        if span.get("measure") not in ("WALL_INTERVAL", "DECLARED_ACTIVE_HUMAN_INTERVAL"):
            raise AccountError("Unknown time measure")
        if span["measure"] == "DECLARED_ACTIVE_HUMAN_INTERVAL" and span["actor_kind"] != "HUMAN":
            raise AccountError("Only human intervals can be declared active human effort")
        a = timestamp(span["start_utc"])
        z = timestamp(span["finish_utc"]) if span["finish_utc"] else None
        if a < start or (finish and a > finish) or (z and z < a) or (finish and z and z > finish):
            raise AccountError(f"Reversed or out-of-bound interval: {span['id']}")
        if finish and z is None:
            raise AccountError("Closed workflow contains an open interval")
        if z and span.get("outcome") not in OUTCOMES:
            raise AccountError("Completed interval needs an outcome")
        if not span.get("evidence"):
            raise AccountError("Interval needs attributable evidence")
        for ref in span["evidence"]:
            check_ref(ref, base)
    charge_keys = set()
    for use in account["usage"]:
        if use.get("kind") not in ("MONEY", "INPUT_TOKENS", "OUTPUT_TOKENS", "CACHED_TOKENS"):
            raise AccountError("Unknown usage kind")
        value = number(use["value"])
        if use.get("component") not in MONEY_COMPONENTS:
            raise AccountError("Unknown usage component")
        if use["kind"] == "MONEY":
            if not use.get("unit") or not use.get("charge_key"):
                raise AccountError("Money needs currency and attributable charge key")
            if use["charge_key"] in charge_keys:
                raise AccountError("One charge must not be counted twice")
            charge_keys.add(use["charge_key"])
        elif use.get("unit") != "tokens" or value != value.to_integral_value():
            raise AccountError("Token usage needs a nonnegative integer and tokens unit")
        check_ref(use["evidence"], base)
        when = timestamp(use["at_utc"])
        if when < start or (finish and when > finish):
            raise AccountError("Usage observation falls outside the workflow boundary")
    for event in account["acceptance"]:
        if event.get("kind") not in KINDS or event.get("decision") not in ("ACCEPTED", "REJECTED", "PENDING"):
            raise AccountError("Unknown acceptance kind or decision")
        if not event.get("item") or not event.get("reviewer"):
            raise AccountError("Acceptance needs logical item and reviewer identity")
        if event["kind"] == "HUMAN" and not event.get("human_attestation"):
            raise AccountError("Human decisions need explicit attribution; an automated pass is insufficient")
        check_ref(event["candidate"], base)
        check_ref(event["evidence"], base)
        when = timestamp(event["at_utc"])
        if when < start or (finish and when > finish):
            raise AccountError("Acceptance observation falls outside the workflow boundary")
    for phase in PHASES:
        entry = account["coverage"][phase]
        if entry.get("state") not in ("UNKNOWN", "OBSERVED", "NOT_PERFORMED", "NOT_APPLICABLE"):
            raise AccountError("Unknown phase coverage state")
        if not entry.get("reason"):
            raise AccountError("Coverage needs a reason")
        if entry["state"] != "UNKNOWN" and not entry.get("evidence"):
            raise AccountError("Known coverage needs evidence")
        if entry["state"] == "OBSERVED" and not any(s["phase"] == phase and s["finish_utc"] for s in account["spans"]):
            raise AccountError("Observed phase needs a completed interval")
        if entry["state"] in ("NOT_PERFORMED", "NOT_APPLICABLE") and any(s["phase"] == phase for s in account["spans"]):
            raise AccountError("Observed interval conflicts with absence declaration")
        for ref in entry.get("evidence", []):
            check_ref(ref, base)
    for component in MONEY_COMPONENTS:
        entry = account["money_coverage"][component]
        if entry.get("state") not in ("UNKNOWN", "COMPLETE", "NOT_APPLICABLE") or not entry.get("reason"):
            raise AccountError("Invalid money coverage")
        matching = [u for u in account["usage"] if u["kind"] == "MONEY" and u["component"] == component]
        if entry["state"] == "COMPLETE" and not matching:
            raise AccountError("Complete money coverage needs at least one attributable amount, including explicit zero")
        if entry["state"] == "NOT_APPLICABLE" and matching:
            raise AccountError("Money amount conflicts with not-applicable component")
        if entry["state"] != "UNKNOWN" and not entry.get("evidence"):
            raise AccountError("Known money coverage needs evidence")
        for ref in entry.get("evidence", []):
            check_ref(ref, base)
    if any(e["kind"] == "HUMAN" and e["decision"] == "ACCEPTED" for e in account["acceptance"]):
        if account["coverage"]["human_review"]["state"] in ("NOT_PERFORMED", "NOT_APPLICABLE"):
            raise AccountError("Human acceptance conflicts with declared absence of human review")
    for assumption in account["assumptions"]:
        if not assumption.get("name") or not assumption.get("basis") or not assumption.get("unit"):
            raise AccountError("An assumption needs a name, unit and basis")
        number(assumption["value"])
    return account


def union_seconds(intervals):
    if not intervals:
        return 0.0
    intervals = sorted(intervals)
    result = 0.0
    a, b = intervals[0]
    for c, d in intervals[1:]:
        if c <= b:
            b = max(b, d)
        else:
            result += (b - a).total_seconds()
            a, b = c, d
    return result + (b - a).total_seconds()


def summarize(account, base=None):
    validate(account, base)
    spans = [s for s in account["spans"] if s["finish_utc"]]
    intervals = [(timestamp(s["start_utc"]), timestamp(s["finish_utc"])) for s in spans]
    actors = defaultdict(list)
    human_active = defaultdict(list)
    for span, interval in zip(spans, intervals):
        actors[span["actor"]].append(interval)
        if span["measure"] == "DECLARED_ACTIVE_HUMAN_INTERVAL":
            human_active[span["actor"]].append(interval)
    raw_sum = sum((z - a).total_seconds() for a, z in intervals)
    union = union_seconds(intervals)
    accepted = {}
    for kind in KINDS:
        latest = {}
        for event in account["acceptance"]:
            if event["kind"] == kind:
                prior = latest.get(event["item"])
                if prior is None or timestamp(event["at_utc"]) >= timestamp(prior["at_utc"]):
                    latest[event["item"]] = event
        accepted[kind] = {
            "accepted_distinct_items": sum(v["decision"] == "ACCEPTED" for v in latest.values()) if latest else None,
            "latest_items": {item: {"decision": v["decision"], "candidate_sha256": v["candidate"]["sha256"],
                                    "evidence": v["evidence"]} for item, v in latest.items()},
        }
    totals = defaultdict(Decimal)
    for entry in account["usage"]:
        if entry["kind"] == "MONEY":
            totals[entry["unit"]] += number(entry["value"])
    complete_money = all(v["state"] != "UNKNOWN" for v in account["money_coverage"].values())
    complete_activity = (bool(account["boundary"]["finish_utc"])
                         and all(v["state"] != "UNKNOWN" for v in account["coverage"].values()))
    single_currency = len(totals) == 1
    total = next(iter(totals.values())) if complete_money and complete_activity and single_currency else None
    denominator = accepted["HUMAN"]["accepted_distinct_items"]
    ratio = total / denominator if total is not None and denominator is not None and denominator > 0 else None
    b = account["boundary"]
    elapsed = ((timestamp(b["finish_utc"]) - timestamp(b["start_utc"])).total_seconds()
               if b["finish_utc"] else None)
    warnings = [f"Unmeasured phase: {p}" for p, v in account["coverage"].items() if v["state"] == "UNKNOWN"]
    warnings += [f"Incomplete monetary component: {p}" for p, v in account["money_coverage"].items() if v["state"] == "UNKNOWN"]
    if len(totals) > 1:
        warnings.append("Multiple currencies remain separate; no exchange rate has been assumed")
    if denominator is None:
        warnings.append("Human acceptance is unobserved; an automated or agent decision cannot supply its denominator")
    elif denominator == 0:
        warnings.append("Zero human-accepted outcomes; cost per accepted outcome is undefined")
    if account["evidence_mode"] == "SYNTHETIC_TEACHING_CASE":
        warnings.append("All specimen values are invented teaching inputs, not field observations")
    return {
        "schema": "esa-workflow-cost-report/v1", "run_id": account["run_id"],
        "evidence_mode": account["evidence_mode"], "claim_scope": CLAIM_SCOPE,
        "identity": account["identity"],
        "status": "VALID_ACCOUNT_WITH_EXPLICIT_LIMITS", "boundary": b,
        "workflow_elapsed_seconds": elapsed,
        "completed_span_count": len(spans), "open_span_count": len(account["spans"]) - len(spans),
        "failed_span_ids": [s["id"] for s in spans if s["outcome"] == "FAILED"],
        "abandoned_span_ids": [s["id"] for s in spans if s["outcome"] == "ABANDONED"],
        "sum_of_interval_seconds_not_elapsed": raw_sum,
        "observed_interval_union_seconds": union,
        "overlap_seconds_removed_from_elapsed_coverage": raw_sum - union,
        "per_actor_interval_union_seconds_not_active_effort": {a: union_seconds(v) for a, v in actors.items()},
        "declared_active_human_seconds_by_person": {a: union_seconds(v) for a, v in human_active.items()},
        "declared_active_human_seconds_total": sum(union_seconds(v) for v in human_active.values()) if human_active else None,
        "acceptance": accepted,
        "observed_money_subtotals_by_currency": {k: str(v) for k, v in totals.items()},
        "observed_usage_records": account["usage"],
        "money_coverage_complete_by_declaration": complete_money,
        "activity_coverage_complete_by_declaration": complete_activity,
        "complete_workflow_money": str(total) if total is not None else None,
        "currency": next(iter(totals)) if single_currency else None,
        "cost_per_human_accepted_item": str(ratio) if ratio is not None else None,
        "assumptions_excluded_from_observed_totals": account["assumptions"],
        "roi": None,
        "roi_reason": "A descriptive account does not establish attributable business benefit or a counterfactual",
        "warnings": warnings,
        "verification_boundary": "Evidence file bytes and accounting consistency are checked. Human identity, true completeness, active model time and provider billing are not independently authenticated.",
    }


def write_json(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if exclusive:
        with path.open("x", encoding="utf-8") as f:
            f.write(data)
        return
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=".account-", delete=False) as f:
        f.write(data)
        temporary = f.name
    os.replace(temporary, path)


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    for command in ("init", "start", "stop", "usage", "accept", "coverage", "money-coverage", "assume", "close", "report"):
        p = sub.add_parser(command)
        p.add_argument("account", type=Path)
        if command == "init":
            for key in ("run-id", "purpose", "interface", "boundary"):
                p.add_argument("--" + key, required=True)
            p.add_argument("--mode", choices=("OBSERVED", "SYNTHETIC_TEACHING_CASE"), default="OBSERVED")
            p.add_argument("--exclusion", action="append", default=[])
        elif command == "start":
            p.add_argument("--id", required=True)
            p.add_argument("--phase", choices=PHASES, required=True)
            p.add_argument("--actor", required=True)
            p.add_argument("--actor-kind", choices=ACTORS, required=True)
            p.add_argument("--measure", choices=("WALL_INTERVAL", "DECLARED_ACTIVE_HUMAN_INTERVAL"), default="WALL_INTERVAL")
            p.add_argument("--evidence", type=Path, required=True)
        elif command == "stop":
            p.add_argument("--id", required=True)
            p.add_argument("--outcome", choices=OUTCOMES, required=True)
            p.add_argument("--evidence", type=Path, required=True)
        elif command == "usage":
            p.add_argument("--id", required=True)
            p.add_argument("--kind", choices=("MONEY", "INPUT_TOKENS", "OUTPUT_TOKENS", "CACHED_TOKENS"), required=True)
            p.add_argument("--component", choices=MONEY_COMPONENTS, required=True)
            p.add_argument("--value", required=True)
            p.add_argument("--unit", required=True)
            p.add_argument("--charge-key")
            p.add_argument("--evidence", type=Path, required=True)
        elif command == "accept":
            for key in ("id", "item", "reviewer"):
                p.add_argument("--" + key, required=True)
            p.add_argument("--kind", choices=KINDS, required=True)
            p.add_argument("--decision", choices=("ACCEPTED", "REJECTED", "PENDING"), required=True)
            p.add_argument("--candidate", type=Path, required=True)
            p.add_argument("--evidence", type=Path, required=True)
            p.add_argument("--human-attestation")
        elif command in ("coverage", "money-coverage"):
            p.add_argument("--category", choices=PHASES if command == "coverage" else MONEY_COMPONENTS, required=True)
            p.add_argument("--state", choices=("UNKNOWN", "OBSERVED", "NOT_PERFORMED", "NOT_APPLICABLE") if command == "coverage" else ("UNKNOWN", "COMPLETE", "NOT_APPLICABLE"), required=True)
            p.add_argument("--reason", required=True)
            p.add_argument("--evidence", type=Path, required=True)
        elif command == "assume":
            for key in ("name", "value", "unit", "basis"):
                p.add_argument("--" + key, required=True)
        elif command == "report":
            p.add_argument("--output", type=Path)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            a = new_account(args.run_id, args.purpose, args.interface, args.boundary, args.mode, args.exclusion)
            validate(a)
            write_json(args.account, a, exclusive=True)
        else:
            a = json.loads(args.account.read_text())
            validate(a, args.account.resolve().parent)
            if args.command == "report":
                report = summarize(a, args.account.resolve().parent)
                if args.output:
                    if args.output.resolve() == args.account.resolve():
                        raise AccountError("Report output must not overwrite its source account")
                    write_json(args.output, report)
                print(json.dumps(report, indent=2))
                return 0
            if a["boundary"]["finish_utc"]:
                raise AccountError("Closed accounts are immutable; retain them and create a new account for later work")
            if args.command == "start":
                a["spans"].append({"id": args.id, "phase": args.phase, "actor": args.actor,
                                   "actor_kind": args.actor_kind, "measure": args.measure,
                                   "start_utc": utc_now(), "finish_utc": None, "outcome": None,
                                   "evidence": [fingerprint(args.evidence, args.account)]})
            elif args.command == "stop":
                span = next((s for s in a["spans"] if s["id"] == args.id), None)
                if span is None or span["finish_utc"]:
                    raise AccountError("Stop requires an existing open interval")
                span.update(finish_utc=utc_now(), outcome=args.outcome)
                ref = fingerprint(args.evidence, args.account)
                span["evidence"].append(ref)
                a["coverage"][span["phase"]] = {"state": "OBSERVED", "reason": "Completed attributed interval; this does not prove the phase contains every relevant activity", "evidence": [ref]}
            elif args.command == "usage":
                a["usage"].append({"id": args.id, "kind": args.kind, "component": args.component,
                                   "value": str(number(args.value)), "unit": args.unit,
                                   "charge_key": args.charge_key, "at_utc": utc_now(),
                                   "evidence": fingerprint(args.evidence, args.account)})
            elif args.command == "accept":
                a["acceptance"].append({"id": args.id, "item": args.item, "kind": args.kind,
                                        "decision": args.decision, "reviewer": args.reviewer,
                                        "candidate": fingerprint(args.candidate, args.account),
                                        "evidence": fingerprint(args.evidence, args.account),
                                        "at_utc": utc_now(), "human_attestation": args.human_attestation})
            elif args.command in ("coverage", "money-coverage"):
                key = "coverage" if args.command == "coverage" else "money_coverage"
                a[key][args.category] = {"state": args.state, "reason": args.reason,
                                          "evidence": [fingerprint(args.evidence, args.account)]}
            elif args.command == "assume":
                a["assumptions"].append({"name": args.name, "value": str(number(args.value)),
                                          "unit": args.unit, "basis": args.basis})
            elif args.command == "close":
                a["boundary"]["finish_utc"] = utc_now()
            validate(a, args.account.resolve().parent)
            write_json(args.account, a)
        print(json.dumps({"status": "RECORDED", "command": args.command, "account": str(args.account)}))
        return 0
    except (AccountError, OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
