"""Validate an explicitly fictional, byte-bound teaching decision.

The fixed author-created fixtures model authority separation; they are not
signatures, a sandbox or authentication of a real person. Runtime code never
creates a new owner decision to make the current source pass.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def identities(root, manifest):
    return {name: digest(Path(root) / name) for name in manifest}


def validate(plan, decision, contract, root=ROOT, candidate_root=None, requirements=None):
    """Check current sources and, after implementation, the actual candidate."""
    findings = []
    if requirements is None:
        requirements = read(Path(root) / "practice/lifecycle/requirements_owner_decision.json")
    if (plan.get("plan_id") != "PLAN-007/v2-TEACHING"
            or plan.get("status") != "PROPOSED_TEACHING_TRANSITION"
            or plan.get("supersedes") != "PLAN-007/v1"):
        findings.append("PLAN_TRANSITION_MISMATCH")
    if (decision.get("origin") != "FICTIONAL_AUTHOR_SUPPLIED_OWNER_DECISION"
            or decision.get("owner_role") != "fictional-technical-owner"
            or decision.get("disposition") != "ACCEPT_DIRECT_FOR_TEACHING_IMPLEMENTATION"
            or decision.get("decision_id") != plan.get("owner_decision_id")):
        findings.append("OWNER_DECISION_REQUIRED")
    if (plan.get("contract_id") != contract.get("contract_id")
            or contract.get("selected_design") != "direct"
            or decision.get("contract_sha256") != sha256(canonical(contract)).hexdigest()):
        findings.append("CONTRACT_IDENTITY_MISMATCH")
    candidate_identity = sha256(canonical(contract.get("candidate_files_sha256", {}))).hexdigest()
    if (decision.get("candidate_identity") != candidate_identity
            or plan.get("candidate_identity") != candidate_identity):
        findings.append("CANDIDATE_IDENTITY_MISMATCH")
    if (requirements.get("origin") != "FICTIONAL_AUTHOR_SUPPLIED_OWNER_DECISION"
            or requirements.get("owner_role") != "fictional-product-policy-owner"
            or requirements.get("decision_id") != plan.get("requirements_decision_id")
            or requirements.get("disposition") != "ACCEPT_SPEC_FOR_TEACHING_ONLY"
            or requirements.get("contract_sha256") != sha256(canonical(contract)).hexdigest()
            or requirements.get("candidate_identity") != candidate_identity
            or any(requirements.get(key) is not False for key in ("real_human_approval", "production_release", "payment_authorized"))):
        findings.append("REQUIREMENTS_OWNER_DECISION_REQUIRED")
    if (plan.get("write_paths") != contract.get("write_paths")
            or set(plan.get("write_paths", [])) != {
                "repo/src/treasury/explanation_alpha.py", "repo/src/treasury/operator_view.py"}):
        findings.append("WRITE_SCOPE_MISMATCH")
    authority = decision.get("authority", {})
    if authority != {"local_teaching_implementation": True, "real_human_approval": False,
                     "production_release": False, "payment_authorized": False}:
        findings.append("AUTHORITY_SCOPE_MISMATCH")
    for name, expected in contract.get("source_files_sha256", {}).items():
        try:
            if digest(Path(root) / name) != expected:
                findings.append("SOURCE_IDENTITY_MISMATCH:" + name)
        except OSError:
            findings.append("SOURCE_MISSING:" + name)
    if not contract.get("source_files_sha256") or not contract.get("candidate_files_sha256"):
        findings.append("IDENTITY_BINDINGS_REQUIRED")
    if candidate_root:
        for name, expected in contract["candidate_files_sha256"].items():
            try:
                if digest(Path(candidate_root) / name) != expected:
                    findings.append("ACTUAL_CANDIDATE_MISMATCH:" + name)
            except OSError:
                findings.append("ACTUAL_CANDIDATE_MISSING:" + name)
    return {"schema": "teaching-plan-transition/v1", "status": "REJECTED" if findings else "AUTHORIZED_TEACHING_IMPLEMENTATION_ONLY",
            "plan_id": plan.get("plan_id"), "owner_decision_id": decision.get("decision_id"),
            "requirements_decision_id": requirements.get("decision_id"),
            "candidate_identity": candidate_identity, "findings": findings,
            "resulting_task_state": "BLOCKED" if findings else "READY",
            "authority": authority}


def controls(plan, decision, contract, root, candidate_root):
    results = []
    cases = []
    label_only = deepcopy(plan)
    label_only["status"] = "APPROVED"
    cases.append(("label_only_unblock_without_owner", label_only, {}, contract))
    wrong_decision = deepcopy(decision)
    wrong_decision["candidate_identity"] = "0" * 64
    cases.append(("decision_for_other_candidate", plan, wrong_decision, contract))
    wrong_contract = deepcopy(contract)
    wrong_contract["selected_design"] = "ports"
    cases.append(("different_architecture_contract", plan, decision, wrong_contract))
    excessive = deepcopy(decision)
    excessive["authority"]["production_release"] = True
    cases.append(("production_authority_escalation", plan, excessive, contract))
    for name, supplied_plan, supplied_decision, supplied_contract in cases:
        result = validate(supplied_plan, supplied_decision, supplied_contract, root, candidate_root)
        results.append({"name": name, "passed": result["status"] == "REJECTED", "observed": result})
    missing_requirements = validate(plan, decision, contract, root, candidate_root, requirements={})
    results.append({"name": "technical_decision_without_requirements_acceptance", "passed": missing_requirements["status"] == "REJECTED", "observed": missing_requirements})
    target = Path(candidate_root) / "repo/src/treasury/operator_view.py"
    original = target.read_bytes()
    try:
        target.write_bytes(original + b"\n# Different candidate bytes: deliberate negative control.\n")
        changed = validate(plan, decision, contract, root, candidate_root)
        results.append({"name": "actual_candidate_changed_after_decision", "passed": changed["status"] == "REJECTED",
                        "observed": changed})
    finally:
        target.write_bytes(original)
    return results
