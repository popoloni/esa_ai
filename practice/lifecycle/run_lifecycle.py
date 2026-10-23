"""Run one fictional approved Treasury change through the existing local lab.

The output is a NEW sibling workspace and retained evidence. No original starter,
protected fixture or prior run is edited. Python's standard library and local Git
are sufficient; this command performs no model, network or production action.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from transition import HERE, ROOT, canonical, controls, digest, read, validate


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def command(workspace, logs, name, arguments, expected=None, expected_rejection=None):
    """Retain the real process output; stop immediately on an unexpected result."""
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run([sys.executable, *map(str, arguments)], cwd=workspace,
                               env=env, capture_output=True, text=True, timeout=180)
    logs.mkdir(parents=True, exist_ok=True)
    (logs / (name + ".stdout.log")).write_text(completed.stdout)
    (logs / (name + ".stderr.log")).write_text(completed.stderr)
    result = json.loads(completed.stdout) if completed.stdout.strip().startswith("{") else {}
    write(logs / (name + ".process.json"), {"command": [sys.executable, *map(str, arguments)],
          "cwd": str(workspace), "returncode": completed.returncode, "status": result.get("status")})
    if expected_rejection:
        if (completed.returncode != 1 or result.get("status") != "FAIL"
                or not any(expected_rejection in finding for finding in result.get("findings", []))):
            raise ValueError("EXPECTED_REJECTION_NOT_OBSERVED:" + name)
        return result
    if completed.returncode or (expected and result.get("status") != expected):
        raise ValueError("STAGE_FAILED:" + name + ":" + str(result.get("findings", completed.stderr[-1000:])))
    return result


def materialize(output):
    workspace = output / "workspace"
    def ignore(directory, names):
        excluded = {".git", "__pycache__", "evidence"}
        return [name for name in names if name in excluded or name.endswith(".pyc")]
    shutil.copytree(ROOT, workspace, ignore=ignore)
    # The shared mapping is the current cumulative route maintained by the lab.
    # Read it in a child process so its ROOT and imports cannot leak into this run.
    script = "import sys,json; sys.path.insert(0,'reader_side/tools'); from integration_core import INPUT_PAIRS; print(json.dumps(INPUT_PAIRS))"
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("PYTHONPATH", None)
    selected = subprocess.run([sys.executable, "-c", script], cwd=workspace, env=env,
                              text=True, capture_output=True, check=True, timeout=30)
    pairs = json.loads(selected.stdout)
    copied = {}
    for stage, (candidate, reference) in pairs.items():
        if stage == "implementation":
            continue  # The writer runs only after the new teaching transition.
        shutil.copyfile(workspace / reference, workspace / candidate)
        copied[candidate] = {"reference": reference, "sha256": digest(workspace / candidate)}
    later = {
        "repo/engineering/release/release_dossier.json": "reader_side/reference_solution/ch10/release_dossier.json",
        "repo/src/treasury/policy_history.py": "reader_side/reference_solution/ch11/policy_history.py",
        "repo/engineering/evolution/policy_delta.json": "reader_side/reference_solution/ch11/policy_delta.json",
        "repo/engineering/operations/deployment.json": "reader_side/reference_solution/ch12/deployment.json",
        "repo/engineering/operations/incident_review.json": "reader_side/reference_solution/ch12/incident_review.json",
    }
    for candidate, reference in later.items():
        shutil.copyfile(workspace / reference, workspace / candidate)
        copied[candidate] = {"reference": reference, "sha256": digest(workspace / candidate)}
    write(output / "MATERIALIZED_WORKED_EXAMPLES.json", {
        "mode": "ISOLATED_CUMULATIVE_WORKED_EXAMPLES", "inputs": copied,
        "meaning": "Authored examples copied into this run only; not evidence that the reader repaired their own candidates."})
    return workspace


def review_artifact(workspace, evidence, contract, review_decision, release):
    archive = evidence / "release/artifacts/current.zip"
    destination = evidence / "released_operator"
    destination.mkdir()
    with zipfile.ZipFile(archive) as source:
        manifest = json.loads(source.read("MANIFEST.json"))
        actual = {name: sha256(source.read(name)).hexdigest() for name in source.namelist() if name != "MANIFEST.json"}
        if actual != contract["release_files_sha256"] or actual != manifest["files_sha256"]:
            raise ValueError("RELEASE_ARTIFACT_CANDIDATE_MISMATCH")
        # Only the exact allowlisted archive members are extracted.
        for name in actual:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read(name))
    with zipfile.ZipFile(evidence / "release/artifacts/previous.zip") as source:
        if "src/treasury/operator_view.py" in source.namelist():
            raise ValueError("PRIOR_ARTIFACT_ALREADY_HAS_NEW_OPERATOR_VIEW")
    decision_identity = sha256(canonical(contract["candidate_files_sha256"])).hexdigest()
    if (review_decision.get("candidate_identity") != decision_identity
            or review_decision.get("origin") != "FICTIONAL_AUTHOR_SUPPLIED_OWNER_DECISION"
            or review_decision.get("reviewer_role") == review_decision.get("maker_role")
            or review_decision.get("release_role") == review_decision.get("maker_role")
            or review_decision.get("scope") != "LOCAL_OPERATOR_PRESENTATION_REHEARSAL_ONLY"
            or release.get("status") != "PASS_LOCAL_RELEASE_REHEARSAL_ONLY"):
        raise ValueError("TEACHING_REVIEW_RELEASE_DECISION_MISMATCH")
    result = command(workspace, evidence / "logs", "operator_archive_review", [
        workspace / "practice/lifecycle/review_operator.py", "--source", destination / "src",
        "--cases", workspace / "practice/lifecycle/operator_cases.json"], "PASS_SELECTED_OPERATOR_CASES")
    candidate_path = workspace / "repo/src/treasury/operator_view.py"
    original = candidate_path.read_bytes()
    try:
        candidate_path.write_bytes(original + b"\n# Deliberate changed-source freshness control.\n")
        command(workspace, evidence / "logs", "stale_operator_release_rejected", [
            "reader_side/tools/release_gate.py", "--rehearsal", evidence / "release"],
            expected_rejection="STALE_INPUT:repo/src/treasury/operator_view.py")
    finally:
        candidate_path.write_bytes(original)
    receipt = {"schema": "teaching-operator-release/v1", "status": "PASS_FICTIONAL_LOCAL_RELEASE",
               "decision_id": review_decision["decision_id"], "candidate_identity": decision_identity,
               "artifact_sha256": digest(archive), "artifact_members_sha256": actual,
               "cp10_rehearsal_sha256": digest(evidence / "release/rehearsal.json"),
               "cp10_review_sha256": digest(evidence / "release_review.json"),
               "operator_review": result["status"], "git_commit": manifest["git_commit"],
               "previous_artifact_lacks_operator_view": True,
               "stale_operator_source_rejected": True,
               "real_human_approval": False, "production_release": False, "payment_authorized": False}
    write(evidence / "OPERATOR_RELEASE.json", receipt)
    return receipt


def operator_story(workspace, evidence, contract):
    """Use actual release source and actual CP12 records, not invented outputs."""
    sys.path.insert(0, str(evidence / "released_operator/src"))
    from treasury.architecture.direct import explain
    from treasury.operator_view import explain_for_operator, explain_record, plain_text
    before = explain("4000.00")
    after = explain_for_operator("4000.00")
    records = {}
    for name in ("S01_seed_history", "S03_seed_current", "S05_control_history", "S06_fault_current", "S07_fault_history", "S08_incident_retry"):
        event = read(evidence / "incident/steps" / (name + ".json"))
        record = event["result"]["record"]
        records[name] = {"process_status": event["result"]["status"], "decision_id": record["decision_id"],
                         "request_key": record["request_key"], "database_path": event["database_path"],
                         "policy_version": record["policy_version"], "view": explain_record(record)}
    for name in ("R02_historical_retry", "R03_current_retry"):
        event = read(evidence / "recovery/steps" / (name + ".json"))
        record = event["result"]["record"]
        records[name] = {"process_status": event["result"]["status"], "decision_id": record["decision_id"],
                         "request_key": record["request_key"], "database_path": event["database_path"],
                         "policy_version": record["policy_version"], "view": explain_record(record)}
    checks = {
        "old_request_keeps_exact_identity": records["S01_seed_history"]["decision_id"] == records["S05_control_history"]["decision_id"] == records["R02_historical_retry"]["decision_id"],
        "current_request_keeps_exact_identity": records["S03_seed_current"]["decision_id"] == records["R03_current_retry"]["decision_id"],
        "old_view_survives_activation_and_recovery": records["S01_seed_history"]["view"] == after == records["S05_control_history"]["view"] == records["R02_historical_retry"]["view"],
        "current_v2_view_survives_recovery": records["S03_seed_current"]["view"] == records["R03_current_retry"]["view"],
        "fault_is_visible_as_wrong_policy": records["S06_fault_current"]["policy_version"] == "BR-001/v1" and records["S03_seed_current"]["policy_version"] == "BR-001/v2",
        "product_has_no_benefit_status": "benefit_status" not in after and all("benefit_status" not in item["view"] for item in records.values()),
    }
    if not all(checks.values()):
        raise ValueError("OPERATOR_HISTORY_CHAIN_MISMATCH")
    result = {"schema": "operator-story/v2", "amount_eur": "4000.00", "before_machine_projection": before,
              "after_operator_projection": after, "events": records, "checks": checks}
    write(evidence / "OPERATOR_STORY.json", result)
    paragraphs = ["SAME INPUT: EUR 4,000.00", "BEFORE (legacy machine projection)", json.dumps(before, indent=2),
                  "AFTER (released operator view)", plain_text(after),
                  "POLICY HISTORY: the same request retains v1; a new request uses v2."]
    for name in ("S01_seed_history", "S03_seed_current", "S05_control_history", "S06_fault_current", "R02_historical_retry", "R03_current_retry"):
        item = records[name]
        paragraphs.extend([name + " / " + item["request_key"] + " / " + item["process_status"], plain_text(item["view"])])
    (evidence / "OPERATOR_STORY.txt").write_text("\n\n".join(paragraphs) + "\n")
    write(evidence / "EVALUATION.json", {"schema": "operator-evaluation/v1", "benefit_status": "HYPOTHESIS_NOT_VALIDATED",
          "human_comprehension": "NOT_MEASURED", "time_saved": "NOT_MEASURED", "payment_authorized": False,
          "observed": "Selected source, released-artifact and actual historical-state projections passed.",
          "next_study": "Ask Treasury operators to identify the queue, reason, governing policy and next action, then compare errors and time with the old display."})
    return result


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    evidence = output / "evidence"
    evidence.mkdir()
    result = {"schema": "approved-teaching-lifecycle/v1", "status": "FAIL", "findings": [],
              "mode": "ISOLATED_CUMULATIVE_WORKED_EXAMPLES", "checkpoints": [],
              "real_human_approval": False, "production_release": False, "payment_authorized": False}
    def checkpoint(stage, details):
        result["checkpoints"].append({"stage": stage, **details})
        write(output / "LIFECYCLE_RESULT.json", result)
        print("CHECKPOINT " + stage, file=sys.stderr, flush=True)
    try:
        plan, decision, contract = (read(HERE / name) for name in ("teaching_plan.json", "technical_owner_decision.json", "operator_contract.json"))
        historical = read(ROOT / "reader_side/reference_solution/delegation_plan.json")
        blocked = next(task for task in historical["tasks"] if task["id"] == "T07-04")
        if blocked["state"] != "BLOCKED":
            raise ValueError("HISTORICAL_NEGATIVE_CONTROL_NOT_BLOCKED")
        write(evidence / "HISTORICAL_PLAN.json", {"plan_id": historical["plan_id"], "task": blocked,
              "source_sha256": digest(ROOT / "reader_side/reference_solution/delegation_plan.json")})
        authorization = validate(plan, decision, contract)
        write(evidence / "TECHNICAL_TRANSITION.json", authorization)
        if authorization["status"] != "AUTHORIZED_TEACHING_IMPLEMENTATION_ONLY":
            raise ValueError("TECHNICAL_TRANSITION_REJECTED:" + str(authorization["findings"]))
        workspace = materialize(output)
        candidate = workspace / "repo/src/treasury/explanation_alpha.py"
        before_hash = digest(candidate)
        shutil.copyfile(workspace / "reader_side/reference_solution/explanation_alpha.py", candidate)
        shutil.copyfile(workspace / "practice/lifecycle/operator_view.py", workspace / "repo/src/treasury/operator_view.py")
        implemented = validate(plan, decision, contract, ROOT, workspace)
        if implemented["status"] != "AUTHORIZED_TEACHING_IMPLEMENTATION_ONLY":
            raise ValueError("IMPLEMENTATION_IDENTITY_REJECTED:" + str(implemented["findings"]))
        negatives = controls(plan, decision, contract, ROOT, workspace)
        write(evidence / "TRANSITION_NEGATIVE_CONTROLS.json", negatives)
        if not all(case["passed"] for case in negatives):
            raise ValueError("TRANSITION_NEGATIVE_CONTROL_ACCEPTED")
        write(evidence / "IMPLEMENTATION.json", {"plan_id": plan["plan_id"], "task": "T07-04/v2", "state": "IMPLEMENTED_AWAITING_REVIEW",
              "candidate_identity": implemented["candidate_identity"], "cp08_before_sha256": before_hash,
              "cp08_after_sha256": digest(candidate), "operator_view_sha256": digest(workspace / "repo/src/treasury/operator_view.py"),
              "meaning": "The actual CP08 repair is reused and extended with a versioned plain-language view."})
        checkpoint("implementation", {"status": "VALIDATED_TEACHING_TRANSITION", "candidate_identity": implemented["candidate_identity"]})
        command(workspace, evidence / "logs", "operator_source_review", ["practice/lifecycle/review_operator.py", "--source", "repo/src", "--cases", "practice/lifecycle/operator_cases.json"], "PASS_SELECTED_OPERATOR_CASES")
        command(workspace, evidence / "logs", "integration_review", ["reader_side/tools/integration_gate.py"], "PASS_REVIEW_GATE_ONLY")
        command(workspace, evidence / "logs", "release_rehearsal", ["reader_side/tools/rehearse_release.py", "--teaching-operator", "--output", evidence / "release"], "READY_FOR_DOSSIER_REVIEW")
        release = command(workspace, evidence / "logs", "release_review", ["reader_side/tools/release_gate.py", "--rehearsal", evidence / "release", "--output", evidence / "release_review.json"], "PASS_LOCAL_RELEASE_REHEARSAL_ONLY")
        receipt = review_artifact(workspace, evidence, contract, read(HERE / "review_release_decision.json"), release)
        checkpoint("local_release", {"status": receipt["status"], "artifact_sha256": receipt["artifact_sha256"]})
        extension = read(HERE / "policy_operations_decision.json")
        if (extension.get("origin") != "FICTIONAL_AUTHOR_SUPPLIED_OWNER_DECISION"
                or extension.get("candidate_identity") != implemented["candidate_identity"]
                or extension.get("scope") != "LOCAL_POLICY_HISTORY_AND_INCIDENT_REHEARSAL_ONLY"
                or any(extension.get(key) is not False for key in ("real_human_approval", "production_release", "payment_authorized"))):
            raise ValueError("POLICY_OPERATIONS_DECISION_MISMATCH")
        write(evidence / "POLICY_OPERATIONS_TRANSITION.json", {
            "status": "AUTHORIZED_FICTIONAL_POLICY_AND_RECOVERY_REHEARSAL",
            "decision": extension, "decision_sha256": digest(HERE / "policy_operations_decision.json"),
            "parent_local_release_sha256": digest(evidence / "OPERATOR_RELEASE.json")})
        evolution = command(workspace, evidence / "logs", "evolution_review", ["reader_side/tools/evolution_gate.py", "--output", evidence / "evolution"], "PASS_POLICY_EVOLUTION_REVIEW_ONLY")
        checkpoint("policy_history", {"status": evolution["status"], "source_sha256": digest(workspace / "repo/src/treasury/policy_history.py")})
        command(workspace, evidence / "logs", "incident_rehearsal", ["reader_side/tools/rehearse_incident.py", "--output", evidence / "incident"], "FAULT_REPRODUCED_REVIEW_ONLY")
        recovery = command(workspace, evidence / "logs", "incident_recovery", ["reader_side/tools/incident_gate.py", "--rehearsal", evidence / "incident", "--output", evidence / "recovery"], "PASS_INCIDENT_RECOVERY_REVIEW_ONLY")
        story = operator_story(workspace, evidence, contract)
        checkpoint("incident_recovery", {"status": recovery["status"], "operator_history_checks": story["checks"],
                    "reconciliation_status": recovery["reconciliation_status"]})
        final = validate(plan, decision, contract, ROOT, workspace)
        if final["findings"]:
            raise ValueError("FINAL_IDENTITY_MISMATCH")
        result["status"] = "PASS_APPROVED_TEACHING_LIFECYCLE"
        result["historical_plan_status"] = "PLAN-007/v1 T07-04 remains BLOCKED"
        result["teaching_plan_status"] = "PLAN-007/v2-TEACHING completed through local recovery"
        result["evidence_sha256"] = {name: digest(evidence / name) for name in (
            "HISTORICAL_PLAN.json", "TECHNICAL_TRANSITION.json", "IMPLEMENTATION.json",
            "TRANSITION_NEGATIVE_CONTROLS.json", "logs/integration_review.stdout.log",
            "logs/operator_source_review.stdout.log", "logs/operator_archive_review.stdout.log",
            "logs/stale_operator_release_rejected.stdout.log", "release/rehearsal.json",
            "release_review.json", "OPERATOR_RELEASE.json", "POLICY_OPERATIONS_TRANSITION.json",
            "evolution/EVOLUTION_RESULT.json", "incident/INCIDENT_SESSION.json",
            "recovery/INCIDENT_RESULT.json", "OPERATOR_STORY.json", "EVALUATION.json")}
        result["open_decisions"] = ["Real operator benefit and comprehension are unmeasured.",
            "The incident ledger remains quarantined pending owner reconciliation; no automatic merge or incident closure.",
            "Production release and real human acceptance remain outside this fictional exercise."]
    except Exception as exc:
        result["findings"].append(type(exc).__name__ + ":" + str(exc))
    write(output / "LIFECYCLE_RESULT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="A new directory outside the companion tree")
    args = parser.parse_args()
    output = args.output.absolute()
    if output.exists() or output.is_symlink() or output.resolve().is_relative_to(ROOT.resolve()):
        parser.error("choose a NEW output directory outside the companion tree")
    result = run(output)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS_APPROVED_TEACHING_LIFECYCLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
