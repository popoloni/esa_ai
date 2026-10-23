"""Check selected artifact fidelity in the same-task SDD exercise.

This reads actual Markdown artifacts against fixed CP04 obligations. It is not
a natural-language proof, vendor validator, OS sandbox or human approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

PRACTICE = Path(__file__).resolve().parent
COMPANION = PRACTICE.parents[1]
SHARED_MANIFEST_SHA256 = "354fa9f799f466d5cab6078dec65dd455b7c3d1360cbbaf2a1c51788e894230d"
FILES = {
    "speckit": {"spec": "spec.md", "plan": "plan.md", "tasks": "tasks.md"},
    "openspec": {
        "spec": "openspec/changes/explain-treasury/specs/explanation/spec.md",
        "plan": "openspec/changes/explain-treasury/design.md",
        "tasks": "openspec/changes/explain-treasury/tasks.md",
        "proposal": "openspec/changes/explain-treasury/proposal.md",
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_text(path: Path, root: Path) -> str:
    """Reject symlink substitutions, including intermediate artifact directories."""
    if not path.is_relative_to(root):
        raise ValueError("artifact outside selected root")
    for current in [path, *path.parents]:
        if current.is_symlink():
            raise ValueError("symlinked artifact path")
        if current == root:
            break
    if not path.is_file():
        raise ValueError("missing artifact")
    return path.read_text(encoding="utf-8")


def shared_issues(shared: Path = PRACTICE / "shared") -> list[str]:
    issues = []
    try:
        manifest_path = shared / "INPUT_MANIFEST.json"
        raw = safe_text(manifest_path, shared)
        if hashlib.sha256(raw.encode()).hexdigest() != SHARED_MANIFEST_SHA256:
            return ["SHARED_MANIFEST_CHANGED"]
        manifest = json.loads(raw)
        for rel, entry in manifest["files"].items():
            copied = shared / rel
            original = COMPANION / entry["companion_source"]
            for kind, path, root in [("COPY", copied, shared), ("CORE", original, COMPANION)]:
                try:
                    text = safe_text(path, root)
                    if hashlib.sha256(text.encode()).hexdigest() != entry["sha256"]:
                        issues.append(f"SHARED_{kind}_CHANGED:{rel}")
                except (OSError, ValueError):
                    issues.append(f"SHARED_{kind}_UNREADABLE:{rel}")
    except (OSError, ValueError, KeyError, TypeError):
        issues.append("SHARED_INPUTS_UNREADABLE")
    return issues


def normalized(text: str) -> str:
    return " ".join(text.split())


def parse_cases(text: str) -> tuple[dict[str, dict[str, object]], list[str]]:
    cases, issues = {}, []
    pattern = r"^#### Scenario: (SC-EXPL-\d{3})\s*\n(.*?)(?=^#### Scenario:|^### Requirement:|\Z)"
    for match in re.finditer(pattern, text, re.M | re.S):
        sid, block = match.groups()
        if sid in cases:
            issues.append(f"DUPLICATE_CASE:{sid}")
        names = {
            "input_amount_eur": "amount_eur",
            "expected_route": "route",
            "expected_reason": "reason",
            "expected_policy_version": "policy",
            "payment_authorized": "payment_authorized",
            "notice": "notice",
        }
        record = {}
        for field, label in names.items():
            values = re.findall(r"\b" + label + r" = `([^`]+)`", block)
            if len(values) != 1:
                issues.append(f"MALFORMED_CASE:{sid}:{field}")
                continue
            record[field] = values[0]
        value = record.get("payment_authorized")
        record["payment_authorized"] = False if value == "false" else True if value == "true" else value
        link = re.findall(r"^- Requirement: (REQ-EXPL-\d{3})\s*$", block, re.M)
        if len(link) != 1:
            issues.append(f"MALFORMED_CASE:{sid}:requirement_id")
        else:
            record["requirement_id"] = link[0]
        if "payment authorization is a separate human process" not in block:
            issues.append(f"CASE_AUTHORITY_BOUNDARY_MISSING:{sid}")
        cases[sid] = record
    return cases, issues


def check_flow(root: Path, flow: str, contract: dict, oracle: dict) -> dict:
    issues, texts, inventory = [], {}, {}
    flow_root = root / flow
    for role, rel in {**FILES[flow], "origin": "ORIGIN.json"}.items():
        path = flow_root / rel
        try:
            texts[role] = safe_text(path, root)
            inventory[f"{flow}/{rel}"] = {"sha256": sha(path), "bytes": path.stat().st_size}
        except (OSError, ValueError) as exc:
            issues.append(f"ARTIFACT_UNREADABLE:{role}:{exc}")
    if len(texts) != len(FILES[flow]) + 1:
        return {"flow": flow, "status": "FAIL", "issues": issues, "artifacts": inventory}
    try:
        origin = json.loads(texts["origin"])
        if origin.get("origin") != "author_exercise" or origin.get("named_agent_execution") is not False:
            issues.append("EXERCISE_ORIGIN_MISREPRESENTED")
        if origin.get("model") is not None or origin.get("human_review") != "pending":
            issues.append("UNOBSERVED_MODEL_OR_HUMAN_ACCEPTANCE")
        if origin.get("shared_manifest_sha256") != SHARED_MANIFEST_SHA256:
            issues.append("ORIGIN_SHARED_INPUT_IDENTITY_MISMATCH")
    except (ValueError, TypeError, AttributeError):
        issues.append("ORIGIN_UNREADABLE")

    spec = texts["spec"]
    expected_meta = {
        "Status": contract["status"], "Contract": contract["spec_id"],
        "Discovery": f"{contract['discovery_id']} — {contract['discovery_verdict']}",
        "Policy": contract["policy_version"], "Policy authority": contract["policy_authority"],
        "Decision owner": contract["decision_owner"], "Policy owner": contract["policy_owner"],
        "Value status": contract["value_status"],
        "Out of scope": ", ".join(contract["scope_out"]),
    }
    for key, expected in expected_meta.items():
        values = re.findall(r"^" + re.escape(key) + r": (.+)$", spec, re.M)
        if values != [expected]:
            issues.append(f"CONTRACT_METADATA_MISMATCH:{key}")
    for question in contract["unresolved_questions"]:
        if "- " + question not in spec:
            issues.append(f"OPEN_QUESTION_MISSING:{question}")

    blocks = {}
    for m in re.finditer(r"^### Requirement: (REQ-EXPL-\d{3})[^\n]*\n(.*?)(?=^### Requirement:|\Z)", spec, re.M | re.S):
        rid, body = m.groups()
        if rid in blocks:
            issues.append(f"DUPLICATE_REQUIREMENT:{rid}")
        blocks[rid] = body
    required = {r["id"]: r for r in contract["requirements"]}
    for rid in sorted(set(blocks) - set(required)):
        issues.append(f"UNEXPECTED_REQUIREMENT:{rid}")
    for rid, req in required.items():
        if rid not in blocks:
            issues.append(f"MISSING_REQUIREMENT:{rid}")
            continue
        block = blocks[rid]
        statement = block.strip().split("\n\n", 1)[0]
        if normalized(statement) != normalized(req["statement"]):
            issues.append(f"FIXED_OBLIGATION_WORDING_CHANGED:{rid}")
        if f"Sources: {', '.join(req['source_ids'])}" not in block or f"Owner: {req['owner']}" not in block:
            issues.append(f"REQUIREMENT_SOURCE_OR_OWNER_MISMATCH:{rid}")
        for role in ["plan", "tasks"]:
            if rid not in texts[role]:
                issues.append(f"OBLIGATION_TRACE_MISSING:{role}:{rid}")

    cases, case_issues = parse_cases(spec)
    issues.extend(case_issues)
    wanted = {c["id"]: c for c in oracle["cases"]}
    for sid in sorted(set(cases) - set(wanted)):
        issues.append(f"UNEXPECTED_CASE:{sid}")
    for sid, expected in wanted.items():
        if sid not in cases:
            issues.append(f"MISSING_CASE:{sid}")
            continue
        for field, value in expected.items():
            if field != "id" and cases[sid].get(field) != value:
                issues.append(f"CASE_VALUE_MISMATCH:{sid}:{field}")
        if cases[sid].get("notice") != "ROUTING_ONLY_NOT_PAYMENT_APPROVAL":
            issues.append(f"CASE_NOTICE_MISMATCH:{sid}")
    if "BLOCKED_PENDING_HUMAN_REQUIREMENTS_REVIEW" not in texts["tasks"]:
        issues.append("TASK_AUTHORITY_STATE_MISSING")
    if re.search(r"^- \[[xX]\] T01\b", texts["tasks"], re.M):
        issues.append("UNOBSERVED_HUMAN_REVIEW_MARKED_COMPLETE")
    return {
        "flow": flow, "status": "FAIL" if issues else "PASS",
        "issues": issues, "requirements_present": sorted(blocks),
        "cases_present": sorted(cases), "case_values": cases, "artifacts": inventory,
        "scope": "Fixed wording, metadata, source/owner trace and selected case values in the actual Markdown; no semantic or human-acceptance proof.",
    }


def compare(root: Path) -> dict:
    root = root.absolute()
    integrity = shared_issues()
    if integrity:
        return {"status": "FAIL", "shared_input_issues": integrity, "flows": [], "human_review": "pending"}
    contract = json.loads((PRACTICE / "shared/specification.json").read_text())
    oracle = json.loads((PRACTICE / "shared/case_oracle.json").read_text())
    flows = [check_flow(root, name, contract, oracle) for name in FILES]
    pair_equal = flows[0].get("case_values") == flows[1].get("case_values")
    return {
        "format_version": 1, "status": "PASS" if all(f["status"] == "PASS" for f in flows) else "FAIL",
        "artifact_root": str(root), "shared_manifest_sha256": SHARED_MANIFEST_SHA256,
        "shared_input_issues": [], "flows": flows, "pair_case_values_equal": pair_equal,
        "pair_equality_is_sufficient": False, "human_review": "pending",
        "named_agent_execution": False, "framework_performance_comparison": False,
        "interpretation": "Each flow is checked against unchanged external exercise obligations before parity is reported. Agreement between two incomplete artifacts is not acceptance.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True, type=Path, help="Directory containing speckit/ and openspec/ artifacts")
    parser.add_argument("--json", action="store_true", help="Emit the complete machine-readable report")
    args = parser.parse_args()
    report = compare(args.artifacts)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for finding in report.get("shared_input_issues", []):
            print(finding)
        for flow in report["flows"]:
            print(f"{flow['flow']}: {flow['status']} ({len(flow['issues'])} finding(s))")
            for finding in flow["issues"]:
                print("  " + finding)
        print("Human requirements approval: PENDING. Named-agent generation: NOT_RUN.")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
