"""Observed local CP13 attempts, exact scenario acceptance and bounded economics."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from incident_core import (ROOT, safe_owned_path, tree_hashes, checked_evidence,
    read_json, write_json, canonical, digest, environment, validate_session)
from learning_core import (source_inputs as learning_inputs, validate_transfer,
    REVIEW as LEARNING_REVIEW, KNOWLEDGE as LEARNING_KNOWLEDGE,
    REFERENCE_REVIEW as LEARNING_REFERENCE_REVIEW, REFERENCE_KNOWLEDGE as LEARNING_REFERENCE_KNOWLEDGE,
    SUCCESS as LEARNING_SUCCESS, TRANSFER_SUCCESS)
from integration_core import INPUT_PAIRS, SHARED_INPUTS
from scope_guard import check_integrity, check_edit_scope, check_candidate_path
from measurement_costs import calculate_scenarios

REVIEW = "repo/engineering/measurement/outcome_review.json"
DECISION = "repo/engineering/measurement/tool_decision.json"
REFERENCE_REVIEW = "reader_side/reference_solution/ch14/outcome_review.json"
REFERENCE_DECISION = "reader_side/reference_solution/ch14/tool_decision.json"
UNSAFE_REVIEW = "reader_side/measurement/unsafe_outcome_review.json"
UNSAFE_DECISION = "reader_side/measurement/unsafe_tool_decision.json"
PROTOCOL = "reader_side/measurement/protocol.json"
COSTS = "reader_side/measurement/cost_scenarios.json"
OWNER = "reader_side/measurement/owner_acceptance.json"
CAPABILITIES = "reader_side/measurement/tool_capabilities.json"
SUCCESS = "PASS_MEASUREMENT_REVIEW_ONLY"
RECORDED = "MEASUREMENT_RECORDED_REVIEW_ONLY"
GATE_COMMANDS = [("A01", "learning_gate"), ("A02", "learning_gate"), ("A03", "learning_gate"),
                 ("A04", "rehearse_transfer"), ("A04", "learning_gate"), ("A05", "learning_gate")]


def new_output(path, root=ROOT, inputs=()):
    path = safe_owned_path(path, root)
    if any(path.is_relative_to(Path(value).absolute()) for value in inputs):
        raise ValueError("OUTPUT_MUST_NOT_NEST_IN_PRIOR_EVIDENCE")
    path.mkdir(parents=True, exist_ok=False)
    return path


def source_inputs(root, reference=False):
    root = Path(root)
    values = learning_inputs(root, reference)
    paths = set(SHARED_INPUTS) | {pair[int(reference)] for pair in INPUT_PAIRS.values()}
    paths.update((LEARNING_REFERENCE_REVIEW, LEARNING_REFERENCE_KNOWLEDGE) if reference else (LEARNING_REVIEW, LEARNING_KNOWLEDGE))
    paths.update((PROTOCOL, COSTS, OWNER, CAPABILITIES, "reader_side/measurement/WORK_ORDER_CP14.md"))
    values.update({name: digest(root / name) for name in sorted(paths)})
    return values


def append_event(directory, value):
    raw = Path(directory) / "raw"
    raw.mkdir(exist_ok=True)
    earlier = sorted(raw.glob("*.json"))
    event = {"schema": "cp14-observation-event/v1", "sequence": len(earlier) + 1,
             "previous_sha256": digest(earlier[-1]) if earlier else None, **value}
    target = raw / f"{len(earlier) + 1:06d}.json"
    with target.open("x") as stream:
        stream.write(canonical(event) + "\n")
    return event


def command_event(directory, working, attempt, label, arguments, report):
    events = sorted((Path(directory) / "raw").glob("*.json"))
    command_id = f"C{1 + sum(read_json(path).get('kind') == 'COMMAND' for path in events):02d}"
    logs = Path(directory) / "logs"
    logs.mkdir(exist_ok=True)
    command = [sys.executable, "-B", *map(str, arguments)]
    selected_reference = "--reference" in arguments or "--unsafe-control" in arguments
    inputs = source_inputs(working, selected_reference)
    if "--unsafe-control" in arguments:
        inputs.update({name: digest(Path(working) / name) for name in
                       ("reader_side/learning/unsafe_transfer_review.json", "reader_side/learning/unsafe_team_knowledge.json")})
    start_utc = datetime.now(timezone.utc).isoformat()
    start = time.monotonic_ns()
    try:
        run = subprocess.run(command, cwd=working, env=environment(), capture_output=True, text=True, timeout=180)
        code, stdout, stderr = run.returncode, run.stdout, run.stderr
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr = 124, str(exc.stdout or ""), "Timeout after 180 seconds"
    end = time.monotonic_ns()
    for suffix, text in (("stdout", stdout), ("stderr", stderr)):
        with (logs / (command_id + "." + suffix + ".log")).open("x") as stream:
            stream.write(text)
    try:
        result = read_json(report) if Path(report).is_file() else {}
    except (ValueError, OSError):
        result = {}
    value = {"kind": "COMMAND", "command_id": command_id, "attempt_id": attempt, "command_label": label,
             "argv": command, "started_at_utc": start_utc, "monotonic_start_ns": start,
             "monotonic_end_ns": end, "elapsed_ns": end - start, "returncode": code,
             "result_status": result.get("status") if isinstance(result, dict) else None,
             "result_relative_path": Path(report).relative_to(directory).as_posix(),
             "result_sha256": digest(report) if Path(report).is_file() else None,
             "stdout_sha256": digest(logs / (command_id + ".stdout.log")),
             "stderr_sha256": digest(logs / (command_id + ".stderr.log")),
             "execution_input_receipts": inputs,
             "execution_inputs_unchanged": all(digest(Path(working) / name) == value for name, value in inputs.items()),
             "human_effort_hours": None, "vendor_cost": None,
             "quantity_origin": "OBSERVED_LOCAL_PROCESS_CLOCK"}
    append_event(directory, value)
    return result


def _learning_paths(reference):
    return (LEARNING_REFERENCE_REVIEW, LEARNING_REFERENCE_KNOWLEDGE) if reference else (LEARNING_REVIEW, LEARNING_KNOWLEDGE)


def artifact_identity(root, reference, transfer):
    return {"logical_item_id": "HANDOFF-013",
            "selected_candidate_sha256": {name: digest(Path(root) / name) for name in _learning_paths(reference)},
            "transfer_session_sha256": digest(Path(transfer) / "TRANSFER_SESSION.json")}


def rehearse_measurement(incident, transfer, output, root=ROOT, reference=False):
    root = Path(root).resolve()
    incident, transfer = safe_owned_path(incident, root), safe_owned_path(transfer, root)
    output = new_output(output, root, (incident, transfer))
    original = {"incident": tree_hashes(incident), "transfer": tree_hashes(transfer)}
    result = {"schema": "cp14-measurement-session/v1", "status": "FAIL", "mode": "PROTECTED_REFERENCE" if reference else "WORKING_CANDIDATES",
              "findings": [], "checks": [], "source_inputs": source_inputs(root, reference),
              "human_effort": "UNKNOWN", "vendor_billing": "UNKNOWN", "real_human_acceptance": "UNKNOWN",
              "meaning": "Measured local process telemetry and protected synthetic scenario acceptance; no field productivity or economic result."}
    try:
        integrity = check_integrity(root)
        if integrity:
            raise ValueError("PROTECTED_INTEGRITY:" + ",".join(integrity))
        _, issues, _ = validate_session(incident, root, reference)
        seed_record, transfer_issues, _ = validate_transfer(transfer, root, reference)
        if issues or transfer_issues:
            raise ValueError("PREREQUISITE_EVIDENCE:" + ",".join(issues + transfer_issues))
        if seed_record["learning_session_sha256"] != digest(incident / "INCIDENT_SESSION.json"):
            raise ValueError("CP12_CP13_SOURCE_SESSION_MISMATCH")
        shutil.copytree(incident, output / "inputs/incident")
        shutil.copytree(transfer, output / "inputs/transfer")
        result["incident_session_sha256"] = digest(incident / "INCIDENT_SESSION.json")
        result["seed_transfer_session_sha256"] = digest(transfer / "TRANSFER_SESSION.json")
        with tempfile.TemporaryDirectory(prefix="cp14-workflow-") as directory:
            working = Path(directory) / "companion"
            shutil.copytree(root, working, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "evidence"))
            selected = _learning_paths(reference)
            current_bytes = {name: (working / name).read_bytes() for name in selected}
            (output / "artifacts/selected_source").mkdir(parents=True)
            for name, raw in current_bytes.items():
                (output / "artifacts/selected_source" / Path(name).name).write_bytes(raw)
            if not reference:
                for candidate, fixture in ((LEARNING_REVIEW, "unsafe_transfer_review.json"), (LEARNING_KNOWLEDGE, "unsafe_team_knowledge.json")):
                    (working / candidate).write_bytes((working / "reader_side/learning" / fixture).read_bytes())
            append_event(output, {"kind": "CANDIDATE_ACTION", "action": "SELECT_PROTECTED_UNSAFE" if reference else "INSTALL_UNSAFE_IN_DISPOSABLE_COPY",
                                 "logical_item_id": "HANDOFF-013", "human_effort_hours": None, "accounted_with_attempt": "A01"})
            def gate(attempt, session, prior=None, unsafe=False):
                target = output / "attempts" / attempt
                arguments = ["reader_side/tools/learning_gate.py", "--transfer-session", session, "--output", target]
                if unsafe:
                    arguments.append("--unsafe-control")
                elif reference:
                    arguments.append("--reference")
                if prior:
                    arguments += ["--receipt", prior]
                return command_event(output, working, attempt, "learning_gate", arguments, target / "LEARNING_RESULT.json")
            gate("A01", output / "inputs/transfer", unsafe=reference)
            if not reference:
                for name, raw in current_bytes.items():
                    (working / name).write_bytes(raw)
            append_event(output, {"kind": "CANDIDATE_ACTION", "action": "SELECT_PROTECTED_REFERENCE" if reference else "RESTORE_EXACT_CURRENT_CP13_CANDIDATES",
                                 "logical_item_id": "HANDOFF-013", "candidate_sha256": {name: digest(working / name) for name in selected},
                                 "human_effort_hours": None, "accounted_with_attempt": "A02"})
            gate("A02", output / "inputs/transfer")
            gate("A03", output / "inputs/transfer")
            fresh = output / "refreshed_transfer"
            arguments = ["reader_side/tools/rehearse_transfer.py", "--learning-session", output / "inputs/incident", "--output", fresh]
            if reference:
                arguments.append("--reference")
            command_event(output, working, "A04", "rehearse_transfer", arguments, fresh / "TRANSFER_SESSION.json")
            gate("A04", fresh, output / "attempts/A02/LEARNING_RESULT.json")
            final = gate("A05", fresh)
            result["final_transfer_session_sha256"] = digest(fresh / "TRANSFER_SESSION.json")
            artifact = artifact_identity(root, reference, fresh)
            write_json(output / "artifacts/FINAL_ARTIFACT.json", artifact)
            rule = read_json(root / OWNER)
            accepted = {"schema": "cp14-synthetic-acceptance/v1", "origin": "PROTECTED_SYNTHETIC_OWNER_FIXTURE",
                        "rule_id": rule["rule_id"], "actor_id": rule["actor_id"], "decision": "ACCEPT_SCENARIO_ONLY",
                        "logical_item_id": "HANDOFF-013", "accepted_attempt": "A05",
                        "artifact_sha256": digest(output / "artifacts/FINAL_ARTIFACT.json"),
                        "receipt_sha256": digest(output / "attempts/A05/LEARNING_RESULT.json"),
                        "real_human_acceptance": False, "real_release_authorized": False}
            if final.get("status") != LEARNING_SUCCESS:
                raise ValueError("FINAL_CURRENT_REVIEW_NOT_GREEN")
            write_json(output / "SYNTHETIC_OWNER_ACCEPTANCE.json", accepted)
            append_event(output, {"kind": "SYNTHETIC_OWNER_ACCEPTANCE", "record_sha256": digest(output / "SYNTHETIC_OWNER_ACCEPTANCE.json"),
                                 "logical_item_id": "HANDOFF-013", "accepted_attempt": "A05", "human_acceptance_observed": False})
        checks, telemetry, acceptance = measurement_checks(output, root, reference)
        result["checks"], result["local_telemetry"], result["scenario_acceptance"] = checks, telemetry, acceptance
        result["findings"].extend("MEASUREMENT:" + row["name"] for row in checks if not row["passed"])
        if original != {"incident": tree_hashes(incident), "transfer": tree_hashes(transfer)}:
            result["findings"].append("ORIGINAL_EVIDENCE_CHANGED")
        if source_inputs(root, reference) != result["source_inputs"] or check_integrity(root):
            result["findings"].append("SOURCE_CHANGED_DURING_MEASUREMENT")
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result["findings"].append("MEASUREMENT_ERROR:" + type(exc).__name__ + ":" + str(exc))
    result["status"] = RECORDED if result["checks"] and not result["findings"] else "FAIL"
    result["evidence_sha256"] = tree_hashes(output)
    result["session_id"] = sha256(canonical(result).encode()).hexdigest()
    write_json(output / "MEASUREMENT_SESSION.json", result)
    return result


def load_events(directory):
    directory = Path(directory)
    files = sorted((directory / "raw").glob("*.json"))
    if not files:
        raise ValueError("RAW_EVENTS_MISSING")
    previous, events = None, []
    for index, path in enumerate(files, 1):
        value = read_json(path)
        if (path.name != f"{index:06d}.json" or path.is_symlink() or not isinstance(value, dict)
                or value.get("schema") != "cp14-observation-event/v1" or value.get("sequence") != index
                or value.get("previous_sha256") != previous):
            raise ValueError("RAW_EVENT_SEQUENCE_OR_CHAIN")
        previous = digest(path)
        events.append(value)
    return events


def retained_acceptance(directory, root, reference):
    directory, root = Path(directory), Path(root)
    accepted = read_json(directory / "SYNTHETIC_OWNER_ACCEPTANCE.json")
    rule = read_json(root / OWNER)
    final = read_json(directory / "attempts/A05/LEARNING_RESULT.json")
    artifact = read_json(directory / "artifacts/FINAL_ARTIFACT.json")
    expected = {"schema": "cp14-synthetic-acceptance/v1", "origin": "PROTECTED_SYNTHETIC_OWNER_FIXTURE",
                "rule_id": rule["rule_id"], "actor_id": rule["actor_id"], "decision": "ACCEPT_SCENARIO_ONLY",
                "logical_item_id": "HANDOFF-013", "accepted_attempt": "A05",
                "artifact_sha256": digest(directory / "artifacts/FINAL_ARTIFACT.json"),
                "receipt_sha256": digest(directory / "attempts/A05/LEARNING_RESULT.json"),
                "real_human_acceptance": False, "real_release_authorized": False}
    if canonical(accepted) != canonical(expected):
        raise ValueError("SYNTHETIC_ACCEPTANCE_IDENTITY_OR_AUTHORITY")
    if canonical(artifact) != canonical(artifact_identity(root, reference, directory / "refreshed_transfer")):
        raise ValueError("ACCEPTED_ARTIFACT_IS_NOT_CURRENT")
    if (final.get("status") != LEARNING_SUCCESS or final.get("mode") != ("PROTECTED_REFERENCE" if reference else "WORKING_CANDIDATES")
            or final.get("transfer_session_sha256") != artifact["transfer_session_sha256"]
            or any(final.get("input_receipts", {}).get(name) != value for name, value in artifact["selected_candidate_sha256"].items())):
        raise ValueError("ACCEPTANCE_REQUIRES_CURRENT_FINAL_GREEN_RECEIPT")
    # One work item, not the number of passing attempts or retained receipt files.
    return {"distinct_logical_item_ids": ["HANDOFF-013"], "count": 1,
            "origin": "PROTECTED_SYNTHETIC_OWNER_ACCEPTANCE", "accepted_attempt": "A05",
            "artifact_sha256": expected["artifact_sha256"], "receipt_sha256": expected["receipt_sha256"],
            "real_human_accepted_outcomes": None}


def measurement_checks(directory, root=ROOT, reference=False):
    directory, root = Path(directory), Path(root)
    events = load_events(directory)
    commands = [value for value in events if value.get("kind") == "COMMAND"]
    checks = []
    def add(name, condition, observed=None):
        checks.append({"name": name, "passed": bool(condition), "observed": observed})
    add("all_declared_commands_preserved_in_order", [(v.get("attempt_id"), v.get("command_label")) for v in commands] == GATE_COMMANDS)
    add("all_actions_and_final_acceptance_retained", [event.get("kind") for event in events] ==
        ["CANDIDATE_ACTION", "COMMAND", "CANDIDATE_ACTION", "COMMAND", "COMMAND", "COMMAND", "COMMAND", "COMMAND", "SYNTHETIC_OWNER_ACCEPTANCE"])
    expected_statuses = ["FAIL", LEARNING_SUCCESS, LEARNING_SUCCESS, TRANSFER_SUCCESS, "FAIL", LEARNING_SUCCESS]
    add("command_ids_are_unique_and_sequential", [v.get("command_id") for v in commands] == [f"C{i:02d}" for i in range(1, 7)])
    for index, (event, status) in enumerate(zip(commands, expected_statuses)):
        identifier = event.get("command_id", "MISSING")
        report_path = Path(event["result_relative_path"])
        if report_path.is_absolute() or ".." in report_path.parts:
            raise ValueError("RESULT_PATH_ESCAPE")
        report = read_json(directory / report_path)
        add(identifier + ":outcome", event["result_status"] == status == report.get("status")
            and event["returncode"] == (1 if status == "FAIL" else 0))
        add(identifier + ":raw_evidence_binding", digest(directory / report_path) == event["result_sha256"]
            and all(digest(directory / "logs" / (identifier + "." + suffix + ".log")) == event[suffix + "_sha256"] for suffix in ("stdout", "stderr")))
        add(identifier + ":observed_clock_only", all(type(event.get(k)) is int for k in ("monotonic_start_ns", "monotonic_end_ns", "elapsed_ns"))
            and event["monotonic_end_ns"] >= event["monotonic_start_ns"] > 0
            and event["elapsed_ns"] == event["monotonic_end_ns"] - event["monotonic_start_ns"]
            and event.get("human_effort_hours") is None and event.get("vendor_cost") is None)
        expected_inputs = source_inputs(root, reference)
        if index == 0:
            if reference:
                expected_inputs.update({name: digest(root / name) for name in
                    ("reader_side/learning/unsafe_transfer_review.json", "reader_side/learning/unsafe_team_knowledge.json")})
            else:
                expected_inputs[LEARNING_REVIEW] = digest(root / "reader_side/learning/unsafe_transfer_review.json")
                expected_inputs[LEARNING_KNOWLEDGE] = digest(root / "reader_side/learning/unsafe_team_knowledge.json")
        add(identifier + ":exact_execution_inputs", event.get("execution_input_receipts") == expected_inputs
            and event.get("execution_inputs_unchanged") is True)
    seed, seed_issues, _ = validate_transfer(directory / "inputs/transfer", root, reference)
    fresh, fresh_issues, _ = validate_transfer(directory / "refreshed_transfer", root, reference)
    _, incident_issues, _ = validate_session(directory / "inputs/incident", root, reference)
    incident_sha = digest(directory / "inputs/incident/INCIDENT_SESSION.json")
    add("same_CP12_learning_identity", not seed_issues and not fresh_issues and not incident_issues
        and seed.get("learning_session_sha256") == fresh.get("learning_session_sha256") == incident_sha)
    add("refreshed_transfer_has_new_identity", digest(directory / "inputs/transfer/TRANSFER_SESSION.json")
        != digest(directory / "refreshed_transfer/TRANSFER_SESSION.json"))
    faulty = read_json(directory / "attempts/A01/LEARNING_RESULT.json")
    add("faulty_review_rejected_for_expected_reason", "TRANSFER_REVIEW:root_cause" in faulty.get("findings", [])
        and "TEAM_KNOWLEDGE:claim_dependencies" in faulty.get("findings", []))
    stale = read_json(directory / "attempts/A04/LEARNING_RESULT.json")
    add("old_green_receipt_rejected_for_fresh_transfer", "STALE_RECEIPT:TRANSFER_SESSION" in stale.get("findings", [])
        and "STALE_RECEIPT_SESSION" in stale.get("findings", []))
    acceptance = retained_acceptance(directory, root, reference)
    add("one_final_exact_synthetic_acceptance", acceptance["count"] == 1
        and acceptance["accepted_attempt"] == "A05" and acceptance["real_human_accepted_outcomes"] is None)
    last = events[-1]
    add("synthetic_acceptance_appended_after_attempts", last.get("kind") == "SYNTHETIC_OWNER_ACCEPTANCE"
        and last.get("record_sha256") == digest(directory / "SYNTHETIC_OWNER_ACCEPTANCE.json")
        and last.get("human_acceptance_observed") is False)
    totals = {attempt: sum(v["elapsed_ns"] for v in commands if v["attempt_id"] == attempt) for attempt in sorted({v["attempt_id"] for v in commands})}
    gate_commands = [value for value in commands if value.get("command_label") == "learning_gate"]
    telemetry = {"schema": "cp14-local-telemetry/v1", "origin": "OBSERVED_LOCAL_PROCESS_CLOCK", "top_level_commands": len(commands),
                 "gate_attempts": len(gate_commands), "machine_green_attempts": sum(v.get("result_status") == LEARNING_SUCCESS for v in gate_commands),
                 "machine_rejected_attempts": sum(v.get("result_status") == "FAIL" for v in gate_commands),
                 "elapsed_ns_by_attempt": totals, "total_observed_command_elapsed_ns": sum(totals.values()),
                 "nested_processes_added_again": False, "actual_human_effort_hours": None, "actual_vendor_billing": None,
                 "actual_human_accepted_outcomes": None, "actual_cost_per_accepted_outcome": None,
                 "actual_missingness": "UNKNOWN_NOT_ZERO", "production_delivery_metrics": "NOT_MEASURED"}
    return checks, telemetry, acceptance


def validate_measurement(directory, root=ROOT, reference=False):
    directory, root = safe_owned_path(directory, root), Path(root)
    record = read_json(directory / "MEASUREMENT_SESSION.json")
    if not isinstance(record, dict) or record.get("schema") != "cp14-measurement-session/v1":
        return record, ["MEASUREMENT_SESSION_SCHEMA"], [], None, None
    issues = []
    if record.get("status") != RECORDED or record.get("mode") != ("PROTECTED_REFERENCE" if reference else "WORKING_CANDIDATES"):
        issues.append("MEASUREMENT_STATUS_OR_MODE")
    if record.get("session_id") != sha256(canonical({k: v for k, v in record.items() if k != "session_id"}).encode()).hexdigest():
        issues.append("MEASUREMENT_SESSION_IDENTITY")
    old, current = record.get("source_inputs"), source_inputs(root, reference)
    if not isinstance(old, dict):
        issues.append("MEASUREMENT_SOURCE_INPUTS")
    else:
        issues.extend("STALE_MEASUREMENT_INPUT:" + name for name in sorted(set(old) | set(current)) if old.get(name) != current.get(name))
    issues.extend(checked_evidence(directory, record.get("evidence_sha256"), {"MEASUREMENT_SESSION.json"}))
    checks, telemetry, acceptance = [], None, None
    if not issues:
        checks, telemetry, acceptance = measurement_checks(directory, root, reference)
        issues.extend("MEASUREMENT_RECHECK:" + row["name"] for row in checks if not row["passed"])
        for field, relative in (("incident_session_sha256", "inputs/incident/INCIDENT_SESSION.json"),
                                ("seed_transfer_session_sha256", "inputs/transfer/TRANSFER_SESSION.json"),
                                ("final_transfer_session_sha256", "refreshed_transfer/TRANSFER_SESSION.json")):
            if record.get(field) != digest(directory / relative):
                issues.append("MEASUREMENT_BOUND_SESSION:" + field)
    return record, issues, checks, telemetry, acceptance


def _record_findings(value, expected, prefix):
    if not isinstance(value, dict):
        return [prefix + ":SCHEMA"]
    return [prefix + ":" + key for key in sorted(set(value) | set(expected))
            if canonical(value.get(key)) != canonical(expected.get(key))]


def evaluate_measurement(session, root=ROOT, reference=False, unsafe=False, output=None, receipt=None, scope_baseline=None):
    root = Path(root).resolve()
    if output is None:
        with tempfile.TemporaryDirectory(prefix="cp14-review-") as directory:
            return evaluate_measurement(session, root, reference, unsafe, Path(directory) / "review", receipt, scope_baseline)
    if reference and unsafe:
        raise ValueError("Choose one fixture mode")
    session = safe_owned_path(session, root)
    output = new_output(output, root, (session, *([Path(receipt).absolute().parent] if receipt else [])))
    selected_reference = reference or unsafe
    selected = (UNSAFE_REVIEW, UNSAFE_DECISION) if unsafe else ((REFERENCE_REVIEW, REFERENCE_DECISION) if reference else (REVIEW, DECISION))
    mode = "PROTECTED_UNSAFE_CONTROL" if unsafe else ("PROTECTED_REFERENCE" if reference else "WORKING_CANDIDATES")
    result = {"schema": "cp14-measurement-review/v1", "status": "FAIL", "mode": mode, "measurement_mode": "NOT_READ",
              "findings": [], "checks": [], "edit_scope_checked": scope_baseline is not None,
              "actual_pilot_decision": "CHANGE", "actual_economic_field_result": "UNKNOWN_INCOMPLETE_MEASUREMENTS",
              "human_learning_trial": "PENDING", "rubric_validity": "PENDING_HUMAN_VALIDATION",
              "authority": {"CP07_T07_03": "PENDING_HUMAN", "CP07_T07_04": "BLOCKED", "incident_reconciliation": "PENDING_OWNER",
                            "real_pilot_owner_approval": "PENDING", "procurement_authorized": False, "real_release_authorized": False},
              "meaning": "Observed local workflow and scenario accounting review only. No measured ROI, human productivity, vendor comparison or real acceptance is inferred."}
    issues = result["findings"]
    try:
        issues.extend("PROTECTED_INTEGRITY:" + name for name in check_integrity(root))
        if scope_baseline:
            issues.extend(check_edit_scope(scope_baseline, root=root, chapter="CP14"))
        if not selected_reference:
            for name in (REVIEW, DECISION):
                check_candidate_path(name.removeprefix("repo/"), repo=root / "repo", chapter="CP14")
        inputs = source_inputs(root, selected_reference)
        inputs.update({name: digest(root / name) for name in selected})
        result["input_receipts"] = inputs
        if not issues:
            record, found, checks, telemetry, acceptance = validate_measurement(session, root, selected_reference)
            issues.extend(found)
            result["checks"] = checks
            result["measurement_mode"] = record.get("mode", "INVALID") if isinstance(record, dict) else "INVALID"
            result["measurement_session_sha256"] = digest(session / "MEASUREMENT_SESSION.json")
            for field in ("incident_session_sha256", "seed_transfer_session_sha256", "final_transfer_session_sha256"):
                result[field] = record.get(field) if isinstance(record, dict) else None
        if receipt and result.get("measurement_session_sha256"):
            prior = read_json(receipt)
            if not isinstance(prior, dict) or prior.get("schema") != "cp14-measurement-review/v1":
                issues.append("RECEIPT_SCHEMA")
            else:
                if prior.get("status") != SUCCESS or prior.get("mode") != mode:
                    issues.append("RECEIPT_STATUS_OR_MODE")
                old = prior.get("input_receipts")
                if not isinstance(old, dict):
                    issues.append("RECEIPT_INPUTS_SCHEMA")
                else:
                    issues.extend("STALE_RECEIPT:" + name for name in sorted(set(old) | set(inputs)) if old.get(name) != inputs.get(name))
                if prior.get("measurement_session_sha256") != result["measurement_session_sha256"]:
                    issues.append("STALE_RECEIPT_SESSION")
                issues.extend(checked_evidence(Path(receipt).parent, prior.get("evidence_sha256"), {"MEASUREMENT_RESULT.json"}))
        if not issues:
            costs = calculate_scenarios(read_json(root / COSTS), [row["id"] for row in read_json(root / PROTOCOL)["attempts"]], acceptance["count"])
            result["local_telemetry"], result["scenario_acceptance"], result["scenario_costs"] = telemetry, acceptance, costs
            write_json(output / "LOCAL_TELEMETRY.json", telemetry)
            write_json(output / "SCENARIO_COSTS.json", costs)
            issues.extend(_record_findings(read_json(root / selected[0]), read_json(root / REFERENCE_REVIEW), "OUTCOME_REVIEW"))
            issues.extend(_record_findings(read_json(root / selected[1]), read_json(root / REFERENCE_DECISION), "TOOL_DECISION"))
            result["checks"].append({"name": "all_attempt_scenario_accounting", "passed": costs["total_cost"] == "37.64"
                and [row["conditional_pilot_decision"] for row in costs["scenarios"]] == ["GO", "CHANGE", "STOP"]})
            if not all(row["passed"] for row in result["checks"]):
                issues.append("MEASUREMENT_OR_SCENARIO_CHECK_FAILED")
        if check_integrity(root) or any(digest(root / name) != value for name, value in inputs.items()):
            issues.append("SOURCE_CHANGED_DURING_REVIEW")
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ArithmeticError) as exc:
        issues.append("MEASUREMENT_REVIEW_ERROR:" + type(exc).__name__ + ":" + str(exc))
    result["status"] = SUCCESS if result["checks"] and not issues else "FAIL"
    result["evidence_sha256"] = tree_hashes(output)
    write_json(output / "MEASUREMENT_RESULT.json", result)
    return result
