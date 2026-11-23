"""Derive reached verification stages from fields in a current receipt.

No test, approval or artifact examination is performed by this function.
Absence of evidence is NOT_RUN, never PASS or NOT_APPLICABLE. The latter is
reserved for an explicit scope decision in a separately identified work order.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
CHECK_SCHEMAS = {"esa-prototype-check/v2", "esa-full-mission-check/v1",
                 "esa-offline-candidate-review/v1"}
STAGES = ("startup", "integrity", "contract", "integration", "artifact",
          "authorization")
STATUSES = ("PASS", "FAIL", "NOT_RUN", "NOT_APPLICABLE")


def stage(status, evidence, reason, **extra):
    if status not in STATUSES:
        raise ValueError("Unknown verification status")
    return {"status": status, "evidence": evidence, "reason": reason, **extra}


def derive(report):
    """Return a scoped interpretation without changing any supplied evidence."""
    if report.get("schema") not in CHECK_SCHEMAS:
        return None
    mission = report.get("mission")
    if mission not in {route + str(n) for route in "GB" for n in range(1, 5)}:
        return None
    order = json.loads((ROOT / "orders" / f"mission_{mission}.json").read_text())
    profile = order["evidence_profile"]
    phase = "mission"
    if mission == "B1" and report.get("api_contract") == "B1-API/v2":
        profile, phase = "new_capability", "approved_v2_grammar_extension"
    stages = {
        "startup": stage("PASS", ["schema", "mission", "candidate_path"],
            "The intended runner accepted the entry identity and emitted this "
            "check receipt. This does not establish candidate import."),
        "integrity": stage("NOT_RUN", [], "No integrity result is present."),
        "contract": stage("NOT_RUN", [], "No selected check group ran.",
                          behavior_reached=False),
        "integration": stage("NOT_RUN", [],
            "No continuation or consumer/process observation is present."),
        "artifact": stage("NOT_RUN", [],
            "This receipt has no separate archive/extraction gate. Local "
            "demonstration hashes alone do not establish release fitness."),
        "authorization": stage("NOT_RUN", ["human_acceptance"],
            "No owner acceptance or release authorization is recorded. "
            "Passing checks do not supply that decision."),
    }
    failed_integrity = (
        report.get("status") == "INPUT_INTEGRITY_FAILED"
        or bool(report.get("protected_changes"))
        or report.get("candidate_missing_or_symlink") is True
        or ("candidate_sha256_before" in report
            and report["candidate_sha256_before"] is None)
        or report.get("inputs_unchanged") is False
        or report.get("candidate_retained") is False)
    if failed_integrity:
        stages["integrity"] = stage("FAIL", [name for name in (
            "protected_changes", "candidate_missing_or_symlink",
            "inputs_unchanged", "candidate_retained") if name in report],
            "Protected input, candidate availability or retention failed. "
            "Only check groups actually present below are treated as run.")
    elif report.get("inputs_unchanged") is True:
        stages["integrity"] = stage("PASS", ["inputs_unchanged",
            "candidate_sha256_before", "candidate_sha256_after"],
            "The recorded before/after comparison found inputs unchanged.")
    groups = list(report.get("groups", {}).items())
    supplemental = report.get("supplemental_probe")
    if supplemental and "observation" not in supplemental:
        groups.append(("supplemental_probe", supplemental))
    if groups:
        evidence = ["supplemental_probe" if name == "supplemental_probe"
                    else "groups." + name for name, _ in groups]
        passed = all(group.get("status") == "PASSED" for _, group in groups)
        # unittest's _FailedTest is an import/discovery placeholder, not a
        # candidate assertion. A timed-out process may have reached behavior;
        # incomplete output cannot decide that question.
        timed_out = any(g.get("timed_out") for _, g in groups)
        import_only = all(
            "_FailedTest" in (g.get("stdout", "") + g.get("stderr", ""))
            and not g.get("methods_failed")
            for _, g in groups)
        modules = {"G1": "booking.py", "G2": "booking.py", "G3": "booking.py",
                   "G4": "operations.py", "B1": "src/treasury/routing.py",
                   "B2": "intake.py", "B3": "ledger.py", "B4": "incident.py"}
        candidate_file = str(Path(report["candidate_path"]) / modules[mission])
        trace_pattern = (r'File "' + re.escape(candidate_file)
                         + r'", line [0-9]+, in (?!<module>)')
        candidate_frame = any(re.search(trace_pattern,
            g.get("stdout", "") + g.get("stderr", "")) for _, g in groups)
        known_assertion = any(g.get("methods_failed") or (
            g.get("status") == "PASSED" and g.get("tests_run", 0) > 0)
            for _, g in groups)
        reached = (None if timed_out else False if import_only else
                   True if candidate_frame or known_assertion else None)
        stages["contract"] = stage("PASS" if passed else "FAIL", evidence,
            "Status uses each selected group and any contract-specific "
            "supplemental probe; an import placeholder is not behavioral "
            "evidence. A candidate stack frame or known protected assertion "
            "supports reached behavior; a method count alone does not. "
            "Groups within this stage may retain multiple failures.",
            behavior_reached=reached)
    integration = []
    for name in ("persistence_probe", "context_step"):
        if name in report:
            integration.append((name, report[name].get("succeeded") is True))
    if "demonstration_process" in report:
        run = report["demonstration_process"]
        integration.append(("demonstration_process",
            run.get("returncode") == 0 and not run.get("timed_out")
            and "demonstration" in report))
    if supplemental and "observation" in supplemental:
        integration.append(("supplemental_probe.observation",
            supplemental["observation"].get("succeeded") is True))
    if integration:
        stages["integration"] = stage(
            "PASS" if all(value for _, value in integration) else "FAIL",
            [name for name, _ in integration],
            "An actual continuation or process-boundary probe is retained; "
            "the result applies to this local consumer and candidate only.")
    clean = {key: value for key, value in report.items()
             if key != "verification_progress"}
    return {
        "schema": "esa-verification-progress/v1",
        "derivation": "CURRENT_RECEIPT_FIELDS_ONLY_NO_ADDITIONAL_EXECUTION",
        "source_fields_sha256": hashlib.sha256(json.dumps(
            clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "work_order": f"mission_{mission}", "evidence_profile": profile,
        "profile_basis": ("B1-OD-02 / B1-API/v2 separately authorizes the "
            "new grammar; the base mission work order identifies the v1 repair."
            if phase != "mission" else "The named mission work order."),
        "phase": phase, "stages": stages,
        "first_failed_stage": next((name for name in STAGES
            if stages[name]["status"] == "FAIL"), None),
        "last_observed_stage": next((name for name in reversed(STAGES)
            if stages[name]["status"] in {"PASS", "FAIL"}), None),
        "limits": "A stage label interprets the retained fields; it is not "
            "an independent attestation. NOT_APPLICABLE needs an explicit "
            "scope exclusion; absence alone remains NOT_RUN.",
    }
