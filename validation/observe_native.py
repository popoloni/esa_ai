#!/usr/bin/env python3
"""Prepare and check a native-client evidence packet; never authenticate its claims.

The command recorder is shared with the author package. A complete packet proves
only that the declared evidence files exist and match their recorded identities.
It does not prove that a named client or model produced them, establish OS
containment, grant human acceptance, or close an editorial action automatically.
"""
from pathlib import Path, PurePosixPath
from hashlib import sha256
from datetime import datetime, timezone
import argparse
import json
import shutil
import sys
from record_observed_command import inventory, run

R06_ARTIFACTS = (
    "client_identity", "effective_configuration", "task_prompt", "initial_checks",
    "tool_actions", "first_output", "failure_and_recovery", "final_diff",
    "independent_checks", "reproduction_instructions",
)
R07_ARTIFACTS = (
    "mcp_server_identity", "mcp_opening_exchange", "mcp_tool_discovery",
    "mcp_valid_call", "mcp_invalid_argument", "mcp_domain_refusal",
    "mcp_process_boundary",
)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def local_file(root, relative):
    if not isinstance(relative, str):
        raise ValueError("evidence path must be a string")
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or str(path) != relative or relative == ".":
        raise ValueError("evidence path must be canonical and relative")
    target = root / relative
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("evidence paths cannot contain symlinks")
    if not target.is_file():
        raise ValueError("evidence file is missing: " + relative)
    return target


def prepare(source, output, actions):
    if source.is_symlink() or output.is_symlink():
        raise ValueError("source and output roots cannot be symlinks")
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise ValueError("source must be a directory")
    output = output.resolve()
    if output.exists() or output.is_symlink() or output.is_relative_to(source):
        raise ValueError("choose a new evidence directory outside the source tree")
    before = inventory(source)
    if not before:
        raise ValueError("source inventory is empty")
    if any(value.startswith("SYMLINK:") for value in before.values()):
        raise ValueError("use a disposable source copy without symlinks for this snapshot route")
    output.mkdir(parents=True)
    snapshot = output / "starting_tree"
    for relative in before:
        destination = snapshot / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)
    if inventory(snapshot) != before or inventory(source) != before:
        raise ValueError("source changed during snapshot; preserve this attempt and start a new one")
    manifest = output / "STARTING_MANIFEST.json"
    manifest.write_text(json.dumps(before, indent=2) + "\n")
    record = {
        "schema": "esa-native-observation/v1",
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "record_kind": "UNFILLED_OBSERVATION",
        "execution_kind": "NOT_RUN",
        "actions": actions,
        "client": {"name": None, "version": None, "model_identity": None,
                   "model_identity_availability": "NOT_RECORDED"},
        "prior_solution_exposure": None,
        "contrast": {"status": "UNOBSERVED", "same_contract": None,
                     "meaningful_difference": None, "paired_performance_claim": False},
        "starting_manifest": {"path": manifest.name, "sha256": digest(manifest)},
        "artifacts": {},
        "protocol_era": "NOT_OBSERVED",
        "native_tool_selection": "NOT_RUN",
        "boundary_scope": "NOT_TESTED",
        "unknown_values": [],
        "human_acceptance": "PENDING",
        "structural_check_scope": "EVIDENCE_CONSISTENCY_ONLY_NOT_AUTHENTICITY_OR_ACCEPTANCE",
    }
    path = output / "NATIVE_OBSERVATION.json"
    path.write_text(json.dumps(record, indent=2) + "\n")
    return path


def bind(record_path, key, relative):
    record = json.loads(record_path.read_text())
    if key not in R06_ARTIFACTS + R07_ARTIFACTS:
        raise ValueError("unknown evidence category")
    if key in record["artifacts"]:
        raise ValueError("category already bound; retain first output and create a separate attempt")
    path = local_file(record_path.parent, relative)
    record["artifacts"][key] = {"path": relative, "sha256": digest(path)}
    record_path.write_text(json.dumps(record, indent=2) + "\n")


def inspect(record_path):
    issues = []
    record = json.loads(record_path.read_text())
    if not isinstance(record, dict):
        raise ValueError("observation record must be an object")
    root = record_path.parent
    if record.get("schema") != "esa-native-observation/v1":
        issues.append("UNSUPPORTED_SCHEMA")
    actions = record.get("actions")
    if not isinstance(actions, list) or not actions or any(x not in {"R06", "R07"} for x in actions):
        issues.append("INVALID_ACTION_SCOPE")
        actions = []
    kind = record.get("execution_kind")
    if kind not in {"ACTUAL_NAMED_CLIENT", "OFFLINE_COLLECTOR_REHEARSAL"}:
        issues.append("NO_OBSERVED_EXECUTION_DECLARED")
    client = record.get("client", {})
    if not isinstance(client, dict):
        issues.append("INVALID_CLIENT_RECORD")
        client = {}
    for field in ["name", "version"]:
        value = client.get(field)
        if not isinstance(value, str) or not value.strip() or value == "UNKNOWN_NOT_EXPOSED":
            issues.append("CLIENT_IDENTITY_MISSING:" + field)
    availability = client.get("model_identity_availability")
    if availability not in {"EXPOSED", "NOT_EXPOSED", "NOT_APPLICABLE_REHEARSAL"}:
        issues.append("MODEL_AVAILABILITY_NOT_RECORDED")
    if availability == "EXPOSED" and not client.get("model_identity"):
        issues.append("EXPOSED_MODEL_IDENTITY_MISSING")
    if kind == "ACTUAL_NAMED_CLIENT" and availability == "NOT_APPLICABLE_REHEARSAL":
        issues.append("ACTUAL_CLIENT_CANNOT_USE_REHEARSAL_MODEL_MARKER")
    if not isinstance(record.get("prior_solution_exposure"), str) or not record["prior_solution_exposure"].strip():
        issues.append("SOLUTION_EXPOSURE_NOT_RECORDED")
    contrast = record.get("contrast", {})
    if not isinstance(contrast, dict):
        issues.append("INVALID_CONTRAST_RECORD")
        contrast = {}
    if contrast.get("status") == "UNOBSERVED":
        if contrast.get("paired_performance_claim") is not False:
            issues.append("UNOBSERVED_CONTRAST_CANNOT_SUPPORT_PERFORMANCE_CLAIM")
    elif contrast.get("status") == "OBSERVED":
        if not contrast.get("same_contract") or not contrast.get("meaningful_difference"):
            issues.append("OBSERVED_CONTRAST_DETAILS_MISSING")
    else:
        issues.append("CONTRAST_STATUS_MISSING")
    required = list(R06_ARTIFACTS) if "R06" in actions else []
    if "R07" in actions:
        required += ["client_identity", "effective_configuration", *R07_ARTIFACTS]
        if record.get("protocol_era") not in {"2025-11-25", "2026-07-28", "OTHER_RETAINED_IN_EVIDENCE"}:
            issues.append("PROTOCOL_ERA_NOT_RECORDED")
        if kind == "ACTUAL_NAMED_CLIENT" and record.get("native_tool_selection") != "OBSERVED":
            issues.append("NATIVE_TOOL_SELECTION_UNOBSERVED")
        if not isinstance(record.get("boundary_scope"), str) or record.get("boundary_scope") in {"", "NOT_TESTED"}:
            issues.append("BOUNDARY_OBSERVATION_SCOPE_MISSING")
    artifacts = record.get("artifacts", {})
    if not isinstance(artifacts, dict):
        issues.append("INVALID_ARTIFACTS_RECORD")
        artifacts = {}
    for key in sorted(set(required)):
        reference = artifacts.get(key)
        if not isinstance(reference, dict):
            issues.append("MISSING_EVIDENCE:" + key)
            continue
        try:
            path = local_file(root, reference.get("path"))
            if path.stat().st_size == 0:
                issues.append("EMPTY_EVIDENCE:" + key)
            if digest(path) != reference.get("sha256"):
                issues.append("EVIDENCE_HASH_MISMATCH:" + key)
        except (OSError, ValueError, TypeError) as exc:
            issues.append("INVALID_EVIDENCE:" + key + ":" + str(exc))
    try:
        reference = record["starting_manifest"]
        path = local_file(root, reference["path"])
        if digest(path) != reference.get("sha256"):
            issues.append("STARTING_MANIFEST_HASH_MISMATCH")
        expected = json.loads(path.read_text())
        actual = inventory(root / "starting_tree")
        if not expected or actual != expected:
            issues.append("STARTING_TREE_MISSING_OR_CHANGED")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        issues.append("INVALID_STARTING_TREE:" + str(exc))
    if record.get("structural_check_scope") != "EVIDENCE_CONSISTENCY_ONLY_NOT_AUTHENTICITY_OR_ACCEPTANCE":
        issues.append("CHECK_SCOPE_CHANGED")
    status = "FAIL_EVIDENCE_CONSISTENCY" if issues else (
        "PASS_REHEARSAL_EVIDENCE_CONSISTENCY" if kind == "OFFLINE_COLLECTOR_REHEARSAL"
        else "PASS_DECLARED_NATIVE_EVIDENCE_CONSISTENCY")
    return {
        "schema": "esa-native-evidence-check/v1", "status": status,
        "execution_kind": kind, "issues": issues, "record_sha256": digest(record_path),
        "required_categories": sorted(set(required)),
        "native_authenticity": "NOT_ESTABLISHED_BY_THIS_CHECK",
        "human_acceptance": "NOT_GRANTED_BY_THIS_CHECK",
        "action_closure": "REQUIRES_SEPARATE_REVIEW_AGAINST_ORIGINAL_CRITERIA",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare"); p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--actions", nargs="+", choices=["R06", "R07"], default=["R06", "R07"])
    p = sub.add_parser("capture"); p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("bind"); p.add_argument("record", type=Path)
    p.add_argument("key", choices=R06_ARTIFACTS + R07_ARTIFACTS); p.add_argument("relative_file")
    p = sub.add_parser("check"); p.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            print(prepare(args.source, args.output, args.actions)); return 0
        if args.command == "capture":
            return run(args.spec, args.output)
        if args.command == "bind":
            bind(args.record, args.key, args.relative_file); return 0
        result = inspect(args.record); print(json.dumps(result, indent=2))
        return 1 if result["issues"] else 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    sys.exit(main())
