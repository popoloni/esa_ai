"""CP13 transfer evidence and bounded knowledge review, never a competence grader."""
from hashlib import sha256
from pathlib import Path
import shutil
import sqlite3
import tempfile

from incident_core import (ROOT, CONTROL_CONFIG, REFERENCE_CONFIG, HISTORY, REFERENCE_HISTORY,
    Probe, canonical, digest, read_json, write_json, new_workspace, safe_owned_path,
    snapshot, response_record, route, service_sources, history_source, tree_hashes,
    checked_evidence, validate_session, evaluate_incident, SUCCESS as INCIDENT_SUCCESS)
from scope_guard import check_integrity, check_edit_scope, check_candidate_path

REVIEW = "repo/engineering/learning/transfer_review.json"
KNOWLEDGE = "repo/engineering/learning/team_knowledge.json"
REFERENCE_REVIEW = "reader_side/reference_solution/ch13/transfer_review.json"
REFERENCE_KNOWLEDGE = "reader_side/reference_solution/ch13/team_knowledge.json"
UNSAFE_REVIEW = "reader_side/learning/unsafe_transfer_review.json"
UNSAFE_KNOWLEDGE = "reader_side/learning/unsafe_team_knowledge.json"
PROTOCOL = "reader_side/learning/protocol.json"
RUBRIC = "reader_side/learning/rubric.json"
SUCCESS = "PASS_LEARNING_PROTOCOL_REVIEW_ONLY"
TRANSFER_SUCCESS = "TRANSFER_REPRODUCED_REVIEW_ONLY"
TRANSFER_EVENTS = ["T01_before", "T02_activation", "T03_new_request", "T04_retained_retry",
                   "T05_path_recipe", "T06_explicit_v2", "T07_history"]
RECOVERY_EVENTS = ["U01_restore_v2", "U02_new_request", "U03_history_retry",
                  "U04_current_retry", "U05_recompute", "U06_guard"]


def source_inputs(root, reference):
    names = {REFERENCE_HISTORY if reference else HISTORY,
             "reader_side/reference_solution/ch11/policy_delta.json" if reference else "repo/engineering/evolution/policy_delta.json",
             REFERENCE_CONFIG if reference else "repo/engineering/operations/deployment.json",
             "reader_side/reference_solution/ch12/incident_review.json" if reference else "repo/engineering/operations/incident_review.json",
             "reader_side/reference_solution/context_packet.json" if reference else "repo/engineering/knowledge/context_packet.json",
             "reader_side/reference_solution/context-audit.SKILL.md" if reference else "repo/.agents/skills/context-audit/SKILL.md",
             "repo/src/treasury/routing.py", "reader_side/evolution/policy_catalog.json", PROTOCOL, RUBRIC,
             "reader_side/learning/WORK_ORDER_CP13.md", "reader_side/protected_sha256.json"}
    return {name: digest(Path(root) / name) for name in sorted(names)}


def dependency_receipts(root, reference, transfer):
    return {"POLICY_HISTORY": digest(history_source(root, reference)),
            "POLICY_CATALOG": digest(Path(root) / "reader_side/evolution/policy_catalog.json"),
            "CP12_CONFIG": digest(Path(root) / (REFERENCE_CONFIG if reference else "repo/engineering/operations/deployment.json")),
            "CP12_SESSION": digest(Path(transfer) / "learning_material/INCIDENT_SESSION.json"),
            "TRANSFER_SESSION": digest(Path(transfer) / "TRANSFER_SESSION.json"),
            "RUBRIC": digest(Path(root) / RUBRIC), "PROTOCOL": digest(Path(root) / PROTOCOL),
            "CP06_PACKET": digest(Path(root) / ("reader_side/reference_solution/context_packet.json" if reference else "repo/engineering/knowledge/context_packet.json")),
            "CP06_SKILL": digest(Path(root) / ("reader_side/reference_solution/context-audit.SKILL.md" if reference else "repo/.agents/skills/context-audit/SKILL.md"))}


def affected_claims(changed, dependencies):
    if not isinstance(changed, (list, set, tuple)) or not isinstance(dependencies, dict):
        raise ValueError("INVALID_DEPENDENCIES")
    return sorted(name for name, sources in dependencies.items()
                  if isinstance(sources, list) and set(changed).intersection(sources))


def transfer_checks(directory, root, reference):
    directory = Path(directory)
    events = {name: read_json(directory / "steps" / (name + ".json")) for name in TRANSFER_EVENTS + RECOVERY_EVENTS}
    if not all(isinstance(event, dict) for event in events.values()):
        raise ValueError("TRANSFER_EVENT_SCHEMA")
    checks = []
    def add(name, passed, observed=None):
        checks.append({"name": name, "passed": bool(passed), "observed": observed})
    for name, event in events.items():
        expected_error = "ACTIVE_POLICY_BINDING_MISMATCH" if name == "T05_path_recipe" else None
        add(name + ":observed", event.get("event_id") == name
            and event.get("schema") == "cp12-service-event/v1"
            and event.get("source_sha256") == service_sources(root, history_source(root, reference))
            and event.get("selected_state") == "state/control/history.sqlite"
            and (event.get("status") == "FAIL" and event.get("error") == expected_error
                 if expected_error else event.get("status") == "OK"))
    before = snapshot(directory / "state/preserved/before_activation.sqlite")
    fault = snapshot(directory / "state/control/history.sqlite")
    restored = snapshot(directory / "recovery/state/control/history.sqlite")
    activation = events["T02_activation"]
    add("same_existing_ledger_and_source", events["T01_before"]["database_path"] == events["T03_new_request"]["database_path"]
        and events["T03_new_request"]["database_existed_before"] is True
        and before["active_policy"] == "BR-001/v2" and fault["active_policy"] == "BR-001/v1")
    old_audit = activation["state_before"]["audit_events"]
    new_audit = activation["state_after"]["audit_events"]
    add("observed_activation_is_audited", new_audit[:-1] == old_audit
        and new_audit[-1]["event_type"] == "POLICY_ACTIVATED"
        and new_audit[-1]["evidence_json"] == canonical({"from": "BR-001/v2", "to": "BR-001/v1"}))
    fresh, retry = events["T03_new_request"], events["T04_retained_retry"]
    add("fresh_request_and_retained_retry_differ", fresh.get("result", {}).get("status") == "CREATED"
        and route(fresh) == "STANDARD_QUEUE" and response_record(fresh).get("policy_version") == "BR-001/v1"
        and retry.get("result", {}).get("status") == "REPLAYED" and route(retry) == "HUMAN_REVIEW"
        and response_record(retry).get("policy_version") == "BR-001/v2"
        and retry["state_before"] == retry["state_after"])
    add("path_recipe_does_not_restore_active_policy", events["T05_path_recipe"].get("error") == "ACTIVE_POLICY_BINDING_MISMATCH"
        and events["T05_path_recipe"]["state_before"] == events["T05_path_recipe"]["state_after"])
    add("explicit_v2_behavior_remains_correct", route(events["T06_explicit_v2"]) == "HUMAN_REVIEW"
        and events["T06_explicit_v2"]["state_after"]["active_policy"] == "BR-001/v1")
    for label, earlier, later in (("original_history_retained", before, fault), ("recovery_retains_all_fault_history", fault, restored)):
        by_key = {item["request_key"]: item for item in later["decisions"]}
        add(label, all(by_key.get(item["request_key"]) == item for item in earlier["decisions"])
            and later["audit_events"][:len(earlier["audit_events"])] == earlier["audit_events"])
    add("recovery_restores_active_v2_on_copy", restored["active_policy"] == "BR-001/v2"
        and route(events["U02_new_request"]) == "HUMAN_REVIEW"
        and events["U03_history_retry"]["result"]["status"] == "REPLAYED"
        and events["U04_current_retry"]["result"]["status"] == "REPLAYED"
        and events["U05_recompute"]["result"].get("status") == "MATCH"
        and events["U06_guard"]["result"].get("active_policy") == "BR-001/v2")
    add("fault_state_preserved_after_recovery", digest(directory / "state/control/history.sqlite")
        == digest(directory / "state/preserved/after_activation.sqlite"))
    add("history_recompute_retains_recorded_policy", events["T07_history"]["result"].get("recorded_policy") == "BR-001/v1"
        and events["T07_history"]["result"].get("status") == "MATCH")
    return checks


def rehearse_transfer(learning_session, output, root=ROOT, reference=False):
    root, learning_session = Path(root).resolve(), safe_owned_path(learning_session, root)
    target = safe_owned_path(output, root)
    if target.is_relative_to(learning_session):
        raise ValueError("OUTPUT_MUST_NOT_NEST_IN_LEARNING_EVIDENCE")
    output = new_workspace(target, root)
    result = {"schema": "cp13-transfer-session/v1", "case_id": "TRANSFER-013", "status": "FAIL",
              "mode": "PROTECTED_REFERENCE" if reference else "WORKING_CANDIDATES",
              "findings": [], "checks": [], "human_trial_status": "PENDING",
              "meaning": "Actual local transfer-case process evidence; no human retention or transfer has been measured."}
    try:
        findings = check_integrity(root)
        if findings:
            raise ValueError("PROTECTED_INTEGRITY:" + ",".join(findings))
        result["source_inputs"] = source_inputs(root, reference)
        original_inventory = tree_hashes(learning_session)
        review = evaluate_incident(learning_session, root, reference=reference, output=output / "learning_review")
        if review["status"] != INCIDENT_SUCCESS:
            raise ValueError("CP12_LEARNING_REVIEW_FAILED:" + ",".join(review["findings"]))
        shutil.copytree(learning_session, output / "learning_material")
        result["learning_session_sha256"] = digest(learning_session / "INCIDENT_SESSION.json")
        (output / "state/control").mkdir(parents=True)
        (output / "state/preserved").mkdir(parents=True)
        shutil.copyfile(learning_session / "state/control/history.sqlite", output / "state/control/history.sqlite")
        shutil.copyfile(output / "state/control/history.sqlite", output / "state/preserved/before_activation.sqlite")
        history = history_source(root, reference)
        probe = Probe(root, history, output)
        config, guard = root / CONTROL_CONFIG, root / REFERENCE_CONFIG
        payload = {"amount": "4000.00", "beneficiary": "teaching_supplier"}
        probe.run("T01_before", output, config, "inspect")
        probe.run("T02_activation", output, config, "activate", policy="BR-001/v1")
        probe.run("T03_new_request", output, config, "decide", key="transfer_new_4000", **payload)
        probe.run("T04_retained_retry", output, config, "decide", key="current_4000", **payload)
        probe.run("T05_path_recipe", output, guard, "inspect", expected_error="ACTIVE_POLICY_BINDING_MISMATCH")
        probe.run("T06_explicit_v2", output, config, "decide", key="transfer_explicit_4000", policy="BR-001/v2", **payload)
        probe.run("T07_history", output, config, "recompute", key="historical_4000")
        shutil.copyfile(output / "state/control/history.sqlite", output / "state/preserved/after_activation.sqlite")
        recovery = new_workspace(output / "recovery", root)
        (recovery / "state/control").mkdir(parents=True)
        shutil.copyfile(output / "state/control/history.sqlite", recovery / "state/control/history.sqlite")
        probe.run("U01_restore_v2", recovery, config, "activate", policy="BR-001/v2")
        probe.run("U02_new_request", recovery, config, "decide", key="transfer_recovery_4000", **payload)
        probe.run("U03_history_retry", recovery, config, "decide", key="historical_4000", **payload)
        probe.run("U04_current_retry", recovery, config, "decide", key="current_4000", **payload)
        probe.run("U05_recompute", recovery, config, "recompute", key="historical_4000")
        probe.run("U06_guard", recovery, guard, "inspect")
        probe.checks.extend(transfer_checks(output, root, reference))
        probe.check("original_cp12_evidence_unchanged", tree_hashes(learning_session) == original_inventory)
        result["checks"] = probe.checks
        result["findings"].extend("TRANSFER:" + item["name"] for item in probe.checks if not item["passed"])
        if source_inputs(root, reference) != result["source_inputs"] or check_integrity(root):
            result["findings"].append("SOURCE_CHANGED_DURING_REHEARSAL")
    except (OSError, ValueError, TypeError, KeyError, AttributeError, sqlite3.Error) as exc:
        result["findings"].append("TRANSFER_ERROR:" + type(exc).__name__ + ":" + str(exc))
    result["status"] = TRANSFER_SUCCESS if result["checks"] and not result["findings"] else "FAIL"
    result["evidence_sha256"] = tree_hashes(output)
    result["session_id"] = sha256(canonical(result).encode()).hexdigest()
    write_json(output / "TRANSFER_SESSION.json", result)
    return result


def validate_transfer(directory, root=ROOT, reference=False):
    directory, root = safe_owned_path(directory, root), Path(root).resolve()
    record = read_json(directory / "TRANSFER_SESSION.json")
    if not isinstance(record, dict) or record.get("schema") != "cp13-transfer-session/v1":
        return record, ["TRANSFER_SESSION_SCHEMA"], []
    findings = []
    if record.get("status") != TRANSFER_SUCCESS or record.get("mode") != ("PROTECTED_REFERENCE" if reference else "WORKING_CANDIDATES"):
        findings.append("TRANSFER_STATUS_OR_MODE")
    if record.get("session_id") != sha256(canonical({k: v for k, v in record.items() if k != "session_id"}).encode()).hexdigest():
        findings.append("TRANSFER_SESSION_IDENTITY")
    old, current = record.get("source_inputs"), source_inputs(root, reference)
    if not isinstance(old, dict):
        findings.append("TRANSFER_SOURCE_INPUTS")
    else:
        findings.extend("STALE_TRANSFER_INPUT:" + name for name in sorted(set(old) | set(current)) if old.get(name) != current.get(name))
    findings.extend(checked_evidence(directory, record.get("evidence_sha256"), {"TRANSFER_SESSION.json"}))
    checks = []
    if not findings:
        _, issues, _ = validate_session(directory / "learning_material", root, reference)
        findings.extend("LEARNING_MATERIAL:" + issue for issue in issues)
        if digest(directory / "learning_material/INCIDENT_SESSION.json") != record.get("learning_session_sha256"):
            findings.append("LEARNING_SESSION_IDENTITY")
        try:
            checks = transfer_checks(directory, root, reference)
            findings.extend("TRANSFER_RECHECK:" + item["name"] for item in checks if not item["passed"])
        except (OSError, ValueError, TypeError, KeyError, AttributeError, sqlite3.Error) as exc:
            findings.append("TRANSFER_RECHECK_ERROR:" + type(exc).__name__ + ":" + str(exc))
    return record, findings, checks


def selected_paths(root, reference=False, unsafe=False):
    if reference and unsafe:
        raise ValueError("Choose one fixture mode")
    names = (UNSAFE_REVIEW, UNSAFE_KNOWLEDGE) if unsafe else ((REFERENCE_REVIEW, REFERENCE_KNOWLEDGE) if reference else (REVIEW, KNOWLEDGE))
    return tuple(Path(root) / name for name in names)


def record_findings(supplied, expected, label):
    if not isinstance(supplied, dict):
        return [label + ":SCHEMA"]
    return [label + ":" + key for key in sorted(set(expected) | set(supplied)) if supplied.get(key) != expected.get(key)]


def evaluate_learning(transfer, root=ROOT, reference=False, unsafe=False, output=None, receipt=None, scope_baseline=None):
    root = Path(root).resolve()
    if output is None:
        with tempfile.TemporaryDirectory(prefix="cp13-review-") as directory:
            return evaluate_learning(transfer, root, reference, unsafe, Path(directory) / "review", receipt, scope_baseline)
    target, transfer = safe_owned_path(output, root), safe_owned_path(transfer, root)
    if target.is_relative_to(transfer) or (receipt and target.is_relative_to(Path(receipt).absolute().parent)):
        raise ValueError("OUTPUT_MUST_NOT_NEST_IN_PRIOR_EVIDENCE")
    output = new_workspace(target, root)
    review, knowledge = selected_paths(root, reference, unsafe)
    selected_reference = reference or unsafe
    mode = "PROTECTED_REFERENCE" if reference else ("PROTECTED_UNSAFE_CONTROL" if unsafe else "WORKING_CANDIDATES")
    result = {"schema": "cp13-learning-review/v1", "status": "FAIL", "mode": mode, "transfer_mode": "NOT_READ",
              "findings": [], "checks": [], "edit_scope_checked": scope_baseline is not None,
              "human_delay_trial": "PENDING", "rubric_validity": "PENDING_HUMAN_VALIDATION",
              "human_competence": "NOT_ESTABLISHED_BY_AUTOMATION", "affected_knowledge_claims": [],
              "authority": {"CP07_T07_03": "PENDING_HUMAN", "CP07_T07_04": "BLOCKED", "incident_reconciliation": "PENDING_OWNER",
                            "real_release_authorized": False, "human_competence_certified": False, "incident_closed": False},
              "meaning": "Machine-checked transfer evidence, knowledge dependencies and synthetic pilot calibration. No human learning or rubric validity has been established."}
    issues = result["findings"]
    try:
        issues.extend("PROTECTED_INTEGRITY:" + item for item in check_integrity(root))
        if scope_baseline:
            issues.extend(check_edit_scope(scope_baseline, root=root, chapter="CP13"))
        if not (reference or unsafe):
            for name in (REVIEW, KNOWLEDGE):
                check_candidate_path(name.removeprefix("repo/"), repo=root / "repo", chapter="CP13")
        inputs = source_inputs(root, selected_reference)
        inputs.update({path.relative_to(root).as_posix(): digest(path) for path in (review, knowledge)})
        result["input_receipts"] = inputs
        if not issues:
            result["dependency_receipts"] = dependency_receipts(root, selected_reference, transfer)
            session, issues_found, checks = validate_transfer(transfer, root, selected_reference)
            issues.extend(issues_found)
            result["checks"].extend(checks)
            result["transfer_mode"] = session.get("mode", "INVALID") if isinstance(session, dict) else "INVALID"
            result["transfer_session_sha256"] = digest(transfer / "TRANSFER_SESSION.json")
            result["learning_session_sha256"] = session.get("learning_session_sha256") if isinstance(session, dict) else None
        if receipt and result.get("dependency_receipts"):
            prior = read_json(receipt)
            if not isinstance(prior, dict) or prior.get("schema") != "cp13-learning-review/v1":
                issues.append("RECEIPT_SCHEMA")
            else:
                if prior.get("status") != SUCCESS or prior.get("mode") != mode:
                    issues.append("RECEIPT_STATUS_OR_MODE")
                for field in ("input_receipts", "dependency_receipts"):
                    old = prior.get(field)
                    if not isinstance(old, dict):
                        issues.append("RECEIPT_" + field.upper())
                    else:
                        changed = [name for name in sorted(set(old) | set(result[field])) if old.get(name) != result[field].get(name)]
                        issues.extend("STALE_RECEIPT:" + name for name in changed)
                        if field == "dependency_receipts":
                            result["affected_knowledge_claims"] = affected_claims(changed, read_json(root / REFERENCE_KNOWLEDGE)["claim_dependencies"])
                if prior.get("transfer_session_sha256") != result["transfer_session_sha256"]:
                    issues.append("STALE_RECEIPT_SESSION")
                issues.extend(checked_evidence(Path(receipt).parent, prior.get("evidence_sha256"), {"LEARNING_RESULT.json"}))
        if not issues:
            issues.extend(record_findings(read_json(review), read_json(root / REFERENCE_REVIEW), "TRANSFER_REVIEW"))
            issues.extend(record_findings(read_json(knowledge), read_json(root / REFERENCE_KNOWLEDGE), "TEAM_KNOWLEDGE"))
            from learning_pilot_core import calibrate
            calibration = calibrate(transfer, output / "synthetic_calibration", root)
            result["synthetic_calibration_status"] = calibration["status"]
            result["checks"].append({"name": "synthetic_protocol_calibration", "passed": calibration["status"] == "PASS_SYNTHETIC_CALIBRATION_ONLY"})
            if calibration["status"] != "PASS_SYNTHETIC_CALIBRATION_ONLY":
                issues.append("SYNTHETIC_CALIBRATION_FAILED")
        if check_integrity(root) or any(digest(root / name) != value for name, value in inputs.items()):
            issues.append("SOURCE_CHANGED_DURING_REVIEW")
    except (OSError, ValueError, TypeError, KeyError, AttributeError, sqlite3.Error) as exc:
        issues.append("LEARNING_ERROR:" + type(exc).__name__ + ":" + str(exc))
    result["status"] = SUCCESS if result["checks"] and not issues else "FAIL"
    result["evidence_sha256"] = tree_hashes(output)
    write_json(output / "LEARNING_RESULT.json", result)
    return result
