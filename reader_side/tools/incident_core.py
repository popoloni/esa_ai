"""CP12 owner-run process evidence over the unchanged CP11 SQLite service."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from evolution_core import (catalog, canonical, digest, environment, load_candidate,
                            read_json, safe_database_path, write_json)
from scope_guard import check_candidate_path, check_edit_scope, check_integrity

ROOT = Path(__file__).resolve().parents[2]
CONFIG = "repo/engineering/operations/deployment.json"
REVIEW = "repo/engineering/operations/incident_review.json"
REFERENCE_CONFIG = "reader_side/reference_solution/ch12/deployment.json"
REFERENCE_REVIEW = "reader_side/reference_solution/ch12/incident_review.json"
UNSAFE_CONFIG = "reader_side/operations/unsafe_deployment.json"
UNSAFE_REVIEW = "reader_side/operations/unsafe_incident_review.json"
CONTROL_CONFIG = "reader_side/operations/path_only_control.json"
SCENARIO = "reader_side/operations/scenario.json"
HISTORY = "repo/src/treasury/policy_history.py"
REFERENCE_HISTORY = "reader_side/reference_solution/ch11/policy_history.py"
SUCCESS = "PASS_INCIDENT_RECOVERY_REVIEW_ONLY"
REPRODUCED = "FAULT_REPRODUCED_REVIEW_ONLY"
STATE_PATHS = {"state/control/history.sqlite", "state/incident/history.sqlite"}
EVENTS = ["S01_seed_history", "S01b_seed_anchor", "S02_activate_v2", "S03_seed_current",
          "S04_control_current", "S05_control_history", "S06_fault_current",
          "S07_fault_history", "S08_incident_retry", "S09_explicit_v2", "S10_recompute"]


def safe_owned_path(path, root=ROOT):
    """No source writes or symlink traversal; this is not an OS sandbox."""
    raw = Path(path).absolute()
    if any(part.is_symlink() for part in [raw, *raw.parents]):
        raise ValueError("OWNED_PATH_SYMLINK")
    return safe_database_path(raw, root)


def new_workspace(path, root=ROOT):
    path = safe_owned_path(path, root)
    path.mkdir(parents=True, exist_ok=False)
    write_json(path / "WORKSPACE.json", {"schema": "cp12-owned-workspace/v1",
                                        "incident_id": "INC-012"})
    return path


def known_config(path, root=ROOT):
    root, path = Path(root).resolve(), Path(path).absolute()
    allowed = {root / name for name in (CONFIG, REFERENCE_CONFIG, UNSAFE_CONFIG, CONTROL_CONFIG)}
    if path not in allowed or any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError("CONFIG_PATH_NOT_ALLOWED")
    if path == root / CONFIG:
        check_candidate_path(CONFIG.removeprefix("repo/"), repo=root / "repo", chapter="CP12")
    value = read_json(path)
    fields = {"schema", "deployment_id", "state_path", "initialize_missing_state",
              "expected_active_policy", "required_history_key"}
    if (not isinstance(value, dict) or set(value) != fields
            or value.get("schema") != "cp12-deployment/v1"
            or value.get("deployment_id") != "DEPLOY-012"
            or not isinstance(value.get("state_path"), str) or value.get("state_path") not in STATE_PATHS
            or type(value.get("initialize_missing_state")) is not bool
            or value.get("expected_active_policy") not in (None, "BR-001/v1", "BR-001/v2")
            or value.get("required_history_key") not in (None, "rollout_anchor")):
        raise ValueError("CONFIG_SCHEMA_OR_STATE_PATH")
    return value


def state_path(workspace, relative, root=ROOT):
    workspace = safe_owned_path(workspace, root)
    marker = workspace / "WORKSPACE.json"
    if marker.is_symlink() or read_json(marker) != {"schema": "cp12-owned-workspace/v1", "incident_id": "INC-012"}:
        raise ValueError("OWNED_WORKSPACE_REQUIRED")
    if relative not in STATE_PATHS:
        raise ValueError("STATE_PATH_NOT_ALLOWED")
    target = safe_owned_path(workspace / relative, root)
    if not target.is_relative_to(workspace):
        raise ValueError("STATE_PATH_ESCAPE")
    if target.exists() and not target.is_file():
        raise ValueError("STATE_NOT_FILE")
    return target


def snapshot(path):
    path = Path(path)
    if not path.exists():
        return None
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        tables = {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"decisions", "audit_events", "settings", "policy_versions"}.issubset(tables):
            raise ValueError("STATE_SCHEMA")
        settings = dict(connection.execute("SELECT name,value FROM settings"))
        decisions = [dict(row) for row in connection.execute("SELECT * FROM decisions ORDER BY request_key")]
        audit = [dict(row) for row in connection.execute("SELECT * FROM audit_events ORDER BY event_id")]
        policies = [dict(row) for row in connection.execute("SELECT * FROM policy_versions ORDER BY version")]
        return {"sha256": digest(path), "active_policy": settings.get("active_policy"),
                "decision_count": len(decisions), "audit_count": len(audit),
                "decisions": decisions, "audit_events": audit, "policy_versions": policies}


def history_source(root, reference):
    return Path(root) / (REFERENCE_HISTORY if reference else HISTORY)


def service_sources(root, history):
    return {str(Path(history).relative_to(root)): digest(history),
            "repo/src/treasury/routing.py": digest(Path(root) / "repo/src/treasury/routing.py"),
            "reader_side/evolution/policy_catalog.json": digest(Path(root) / "reader_side/evolution/policy_catalog.json")}


def service_event(workspace, config_path, history, operation, arguments, event_id, root=ROOT):
    """One real worker process calls the selected existing CP11 implementation."""
    root = Path(root).resolve()
    event = {"schema": "cp12-service-event/v1", "event_id": event_id,
             "timestamp_utc": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
             "python_version": sys.version.split()[0], "platform": platform.platform(),
             "operation": operation, "arguments": arguments, "status": "FAIL",
             "payment_authorized": False, "real_release_authorized": False,
             "opentelemetry_sdk_executed": False}
    database, store = None, None
    try:
        integrity = check_integrity(root)
        if integrity:
            raise ValueError("PROTECTED_INTEGRITY:" + ",".join(integrity))
        config = known_config(config_path, root)
        history = Path(history).absolute()
        if history not in {root / HISTORY, root / REFERENCE_HISTORY} or history.is_symlink():
            raise ValueError("HISTORY_PATH_NOT_ALLOWED")
        database = state_path(workspace, config["state_path"], root)
        event.update({"deployment_id": config["deployment_id"], "config": config,
                      "config_sha256": digest(config_path), "source_sha256": service_sources(root, history),
                      "selected_state": config["state_path"], "database_path": str(database),
                      "database_existed_before": database.is_file(), "state_before": snapshot(database)})
        before = event["state_before"]
        # Validate missing state and binding before PolicyStore can initialize it.
        if before is None:
            if not config["initialize_missing_state"]:
                raise ValueError("STATE_MISSING_INITIALIZATION_FORBIDDEN")
            if config["expected_active_policy"] or config["required_history_key"]:
                raise ValueError("STATE_BINDING_UNAVAILABLE")
        else:
            if config["expected_active_policy"] and before["active_policy"] != config["expected_active_policy"]:
                raise ValueError("ACTIVE_POLICY_BINDING_MISMATCH")
            if config["required_history_key"] and config["required_history_key"] not in {r["request_key"] for r in before["decisions"]}:
                raise ValueError("HISTORICAL_ANCHOR_MISSING")
        module = load_candidate(history, root)
        store = module.PolicyStore(database, catalog(root))
        if operation == "inspect":
            result = {"active_policy": store.active_policy()}
        elif operation == "activate":
            result = store.activate(arguments["policy"])
        elif operation == "decide":
            result = store.decide(arguments["key"], {"amount_eur": arguments["amount"],
                                  "beneficiary_id": arguments["beneficiary"]}, arguments.get("policy"))
        elif operation == "replay":
            result = store.replay(arguments["key"])
        elif operation == "recompute":
            result = store.recompute(arguments["key"])
        else:
            raise ValueError("UNKNOWN_OPERATION")
        event.update({"status": "OK", "result": result})
    except Exception as exc:
        event["error"] = getattr(exc, "code", str(exc) if isinstance(exc, ValueError) else type(exc).__name__)
    finally:
        if store is not None:
            store.close()
        if database is not None:
            try:
                event["state_after"] = snapshot(database)
            except (OSError, ValueError, sqlite3.Error) as exc:
                event["status"], event["error"] = "FAIL", "STATE_INSPECTION:" + type(exc).__name__
    return event


def tree_hashes(directory, exclude=()):
    directory = Path(directory)
    result = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError("EVIDENCE_SYMLINK:" + path.relative_to(directory).as_posix())
        if path.is_file() and path.relative_to(directory).as_posix() not in exclude:
            result[path.relative_to(directory).as_posix()] = digest(path)
    return result


def session_inputs(root, reference):
    names = {REFERENCE_HISTORY if reference else HISTORY,
             "reader_side/reference_solution/ch11/policy_delta.json" if reference else "repo/engineering/evolution/policy_delta.json",
             "repo/src/treasury/routing.py", "reader_side/evolution/policy_catalog.json",
             "reader_side/evolution/change_context.json", "reader_side/protected_sha256.json",
             SCENARIO, CONTROL_CONFIG, UNSAFE_CONFIG, "reader_side/operations/WORK_ORDER_CP12.md"}
    return {name: digest(Path(root) / name) for name in sorted(names)}


class Probe:
    def __init__(self, root, history, output):
        self.root, self.history, self.output = Path(root), Path(history), Path(output)
        self.events, self.checks = {}, []

    def check(self, name, condition, observed=None):
        self.checks.append({"name": name, "passed": bool(condition), "observed": observed})

    def run(self, event_id, workspace, config, operation, expected_error=None, **arguments):
        command = [sys.executable, "-B", str(self.root / "reader_side/tools/incident_service.py"),
                   "--workspace", str(workspace), "--config", str(config),
                   "--history", str(self.history), "--event-id", event_id, operation]
        for key, value in arguments.items():
            command += ["--" + key.replace("_", "-"), str(value)]
        try:
            completed = subprocess.run(command, cwd=self.root, env=environment(), text=True,
                                       capture_output=True, timeout=30)
            try:
                event = json.loads(completed.stdout)
                if not isinstance(event, dict):
                    raise ValueError("not an object")
            except ValueError:
                event = {"status": "FAIL", "error": "INVALID_WORKER_OUTPUT"}
            raw = completed.stdout + "\nSTDERR\n" + completed.stderr
            exitcode = completed.returncode
        except subprocess.TimeoutExpired:
            event, raw, exitcode = {"status": "FAIL", "error": "WORKER_TIMEOUT"}, "Worker timed out\n", 124
        write_json(self.output / "steps" / (event_id + ".json"), event)
        (self.output / "steps" / (event_id + ".log")).write_text(raw)
        self.events[event_id] = event
        passed = (exitcode == 1 and event.get("status") == "FAIL" and event.get("error") == expected_error
                  if expected_error else exitcode == 0 and event.get("status") == "OK")
        self.check(event_id + ":process", passed, {"returncode": exitcode, "error": event.get("error")})
        return event


def response_record(event):
    result = event.get("result", {})
    return result.get("record", {}) if isinstance(result, dict) else {}


def route(event):
    return response_record(event).get("decision", {}).get("route")


def causal_checks(events, directory, root, history):
    """Recalculate observations rather than trusting a saved diagnosis verdict."""
    checks = []
    def add(name, condition, observed=None):
        checks.append({"name": name, "passed": bool(condition), "observed": observed})
    for name in EVENTS:
        event = events.get(name, {})
        expected_config = Path(root) / (UNSAFE_CONFIG if name in {"S06_fault_current", "S07_fault_history", "S08_incident_retry", "S09_explicit_v2"} else CONTROL_CONFIG)
        add(name + ":observed", event.get("schema") == "cp12-service-event/v1"
            and event.get("event_id") == name and event.get("status") == "OK"
            and type(event.get("pid")) is int and event.get("pid", 0) > 0
            and event.get("config") == read_json(expected_config)
            and event.get("config_sha256") == digest(expected_config)
            and event.get("source_sha256") == service_sources(root, history))
    first, faulty = events.get("S04_control_current", {}), events.get("S06_fault_current", {})
    config_a, config_b = first.get("config", {}), faulty.get("config", {})
    add("one_variable_state_path_control", {k: v for k, v in config_a.items() if k != "state_path"}
        == {k: v for k, v in config_b.items() if k != "state_path"}
        and config_a.get("state_path") == "state/control/history.sqlite"
        and config_b.get("state_path") == "state/incident/history.sqlite"
        and first.get("arguments") == faulty.get("arguments")
        and first.get("operation") == faulty.get("operation") == "decide"
        and first.get("source_sha256") == faulty.get("source_sha256"))
    add("same_request_different_selected_state", route(first) == "HUMAN_REVIEW" and route(faulty) == "STANDARD_QUEUE"
        and first.get("state_after", {}).get("active_policy") == "BR-001/v2"
        and faulty.get("state_after", {}).get("active_policy") == "BR-001/v1"
        and faulty.get("database_existed_before") is False)
    old, wrong = events.get("S05_control_history", {}), events.get("S07_fault_history", {})
    add("same_deterministic_id_is_not_same_ledger_replay",
        old.get("result", {}).get("status") == "REPLAYED" and wrong.get("result", {}).get("status") == "CREATED"
        and bool(response_record(old).get("decision_id"))
        and response_record(old).get("decision_id") == response_record(wrong).get("decision_id")
        and old.get("database_path") != wrong.get("database_path")
        and wrong.get("state_after", {}).get("audit_count", -2) == wrong.get("state_before", {}).get("audit_count", -4) + 1)
    retry = events.get("S08_incident_retry", {})
    add("same_wrong_ledger_retry_is_idempotent", retry.get("result", {}).get("status") == "REPLAYED"
        and response_record(retry).get("decision_id") == response_record(faulty).get("decision_id")
        and retry.get("state_before") == retry.get("state_after"))
    explicit = events.get("S09_explicit_v2", {})
    add("same_source_explicit_v2_still_routes_correctly", route(explicit) == "HUMAN_REVIEW"
        and response_record(explicit).get("policy_version") == "BR-001/v2"
        and explicit.get("state_after", {}).get("active_policy") == "BR-001/v1"
        and explicit.get("source_sha256") == faulty.get("source_sha256"))
    recompute = events.get("S10_recompute", {})
    add("historical_policy_recomputation_retained", recompute.get("result", {}).get("status") == "MATCH"
        and recompute.get("result", {}).get("recorded_policy") == "BR-001/v1"
        and recompute.get("state_before") == recompute.get("state_after"))
    control = Path(directory) / "state/control/history.sqlite"
    incident = Path(directory) / "state/incident/history.sqlite"
    add("original_state_preserved_during_fault", digest(control) == digest(Path(directory) / "state/preserved/control_before_fault.sqlite")
        and snapshot(control) == old.get("state_after") == recompute.get("state_after"))
    add("incident_state_preserved_separately", digest(incident) == digest(Path(directory) / "state/preserved/incident_after_fault.sqlite")
        and snapshot(incident) == explicit.get("state_after"))
    add("distinct_fresh_worker_processes", len({events.get(name, {}).get("pid") for name in EVENTS}) == len(EVENTS))
    return checks


def rehearse_incident(output, root=ROOT, reference=False):
    root = Path(root).resolve()
    output = new_workspace(output, root)
    mode = "PROTECTED_REFERENCE" if reference else "WORKING_CANDIDATES"
    result = {"schema": "cp12-incident-session/v1", "incident_id": "INC-012", "status": "FAIL",
              "mode": mode, "source_inputs": {}, "findings": [], "checks": [],
              "meaning": "Independently reproduced local synthetic fault; not production incident evidence."}
    try:
        issues = check_integrity(root)
        if issues:
            raise ValueError("PROTECTED_INTEGRITY:" + ",".join(issues))
        result["source_inputs"] = session_inputs(root, reference)
        history = history_source(root, reference)
        probe = Probe(root, history, output)
        scenario = read_json(root / SCENARIO)
        for name in (CONTROL_CONFIG, UNSAFE_CONFIG):
            destination = output / "inputs" / Path(name).name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, destination)
        control, faulty = root / CONTROL_CONFIG, root / UNSAFE_CONFIG
        payload = {"amount": scenario["payload"]["amount_eur"], "beneficiary": scenario["payload"]["beneficiary_id"]}
        probe.run("S01_seed_history", output, control, "decide", key=scenario["history_key"], **payload)
        probe.run("S01b_seed_anchor", output, control, "decide", key=scenario["anchor_key"],
                  amount=scenario["anchor_payload"]["amount_eur"], beneficiary=scenario["anchor_payload"]["beneficiary_id"])
        probe.run("S02_activate_v2", output, control, "activate", policy="BR-001/v2")
        probe.run("S03_seed_current", output, control, "decide", key=scenario["current_key"], **payload)
        probe.run("S04_control_current", output, control, "decide", key=scenario["current_key"], **payload)
        probe.run("S05_control_history", output, control, "decide", key=scenario["history_key"], **payload)
        preserved = output / "state/preserved"
        preserved.mkdir(parents=True)
        shutil.copyfile(output / scenario["control_state"], preserved / "control_before_fault.sqlite")
        probe.run("S06_fault_current", output, faulty, "decide", key=scenario["current_key"], **payload)
        probe.run("S07_fault_history", output, faulty, "decide", key=scenario["history_key"], **payload)
        probe.run("S08_incident_retry", output, faulty, "decide", key=scenario["current_key"], **payload)
        probe.run("S09_explicit_v2", output, faulty, "decide", key=scenario["probe_key"], policy="BR-001/v2", **payload)
        probe.run("S10_recompute", output, control, "recompute", key=scenario["history_key"])
        shutil.copyfile(output / scenario["incident_state"], preserved / "incident_after_fault.sqlite")
        probe.checks.extend(causal_checks(probe.events, output, root, history))
        result["checks"] = probe.checks
        result["findings"].extend("CAUSAL:" + item["name"] for item in probe.checks if not item["passed"])
        if result["source_inputs"] != session_inputs(root, reference) or check_integrity(root):
            result["findings"].append("SOURCE_CHANGED_DURING_REHEARSAL")
    except (OSError, ValueError, TypeError, AttributeError, KeyError, sqlite3.Error) as exc:
        result["findings"].append("REHEARSAL_ERROR:" + type(exc).__name__ + ":" + str(exc))
    result["status"] = REPRODUCED if result["checks"] and not result["findings"] else "FAIL"
    result["evidence_sha256"] = tree_hashes(output)
    result["session_id"] = sha256(canonical(result).encode()).hexdigest()
    write_json(output / "INCIDENT_SESSION.json", result)
    return result


def checked_evidence(directory, inventory, exclude):
    if not isinstance(inventory, dict) or not inventory:
        return ["EVIDENCE_INVENTORY_MISSING"]
    for name, value in inventory.items():
        if not isinstance(name, str) or not isinstance(value, str):
            return ["EVIDENCE_INVENTORY_SCHEMA"]
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or str(relative) != name:
            return ["EVIDENCE_PATH"]
    current = tree_hashes(directory, exclude)
    return ["STALE_EVIDENCE:" + name for name in sorted(set(inventory) | set(current))
            if inventory.get(name) != current.get(name)]


def validate_session(directory, root, reference):
    directory = safe_owned_path(directory, root)
    record = read_json(directory / "INCIDENT_SESSION.json")
    if not isinstance(record, dict) or record.get("schema") != "cp12-incident-session/v1":
        return record, ["SESSION_SCHEMA"], []
    issues = []
    expected_mode = "PROTECTED_REFERENCE" if reference else "WORKING_CANDIDATES"
    if record.get("status") != REPRODUCED or record.get("mode") != expected_mode:
        issues.append("SESSION_STATUS_OR_MODE")
    identity = {k: v for k, v in record.items() if k != "session_id"}
    if record.get("session_id") != sha256(canonical(identity).encode()).hexdigest():
        issues.append("SESSION_IDENTITY")
    old, current = record.get("source_inputs"), session_inputs(root, reference)
    if not isinstance(old, dict):
        issues.append("SESSION_SOURCE_INPUTS")
    else:
        issues.extend("STALE_SESSION_INPUT:" + name for name in sorted(set(old) | set(current)) if old.get(name) != current.get(name))
    issues.extend(checked_evidence(directory, record.get("evidence_sha256"), {"INCIDENT_SESSION.json"}))
    checks = []
    if not issues:
        events = {name: read_json(directory / "steps" / (name + ".json")) for name in EVENTS}
        if not all(isinstance(value, dict) for value in events.values()):
            issues.append("SESSION_EVENT_SCHEMA")
        else:
            checks = causal_checks(events, directory, root, history_source(root, reference))
            issues.extend("CAUSAL_RECHECK:" + item["name"] for item in checks if not item["passed"])
    return record, issues, checks


def selected_paths(root, reference=False, unsafe=False):
    if reference and unsafe:
        raise ValueError("Choose one fixture mode")
    names = (UNSAFE_CONFIG, UNSAFE_REVIEW) if unsafe else ((REFERENCE_CONFIG, REFERENCE_REVIEW) if reference else (CONFIG, REVIEW))
    return tuple(Path(root) / name for name in names)


def review_findings(value, root):
    expected = read_json(Path(root) / REFERENCE_REVIEW)
    if not isinstance(value, dict):
        return ["REVIEW_SCHEMA"]
    return ["INCIDENT_REVIEW:" + field for field in sorted(set(expected) | set(value)) if value.get(field) != expected.get(field)]


def receipt_findings(path, inputs, session_hash, mode):
    prior = read_json(path)
    if not isinstance(prior, dict) or prior.get("schema") != "cp12-incident-review/v1":
        return ["RECEIPT_SCHEMA"]
    issues = []
    if prior.get("status") != SUCCESS or prior.get("mode") != mode:
        issues.append("RECEIPT_STATUS_OR_MODE")
    if prior.get("session_sha256") != session_hash:
        issues.append("STALE_RECEIPT_SESSION")
    old = prior.get("input_receipts")
    if not isinstance(old, dict):
        issues.append("RECEIPT_INPUTS_MISSING")
    else:
        issues.extend("STALE_RECEIPT_INPUT:" + name for name in sorted(set(old) | set(inputs)) if old.get(name) != inputs.get(name))
    issues.extend(checked_evidence(Path(path).parent, prior.get("evidence_sha256"), {"INCIDENT_RESULT.json"}))
    return issues


def recovery_probe(root, history, config, session, output):
    probe = Probe(root, history, output)
    shutil.copytree(Path(session) / "state", output / "state")
    original = snapshot(output / "state/control/history.sqlite")
    incident = snapshot(output / "state/incident/history.sqlite")
    scenario = read_json(root / SCENARIO)
    payload = {"amount": scenario["payload"]["amount_eur"], "beneficiary": scenario["payload"]["beneficiary_id"]}
    inspected = probe.run("R01_inspect", output, config, "inspect")
    old = probe.run("R02_historical_retry", output, config, "decide", key=scenario["history_key"], **payload)
    current = probe.run("R03_current_retry", output, config, "decide", key=scenario["current_key"], **payload)
    recompute = probe.run("R04_historical_recompute", output, config, "recompute", key=scenario["history_key"])
    probe.run("R05_conflict", output, config, "decide", expected_error="IDEMPOTENCY_CONFLICT",
              key=scenario["current_key"], amount="4100.00", beneficiary=payload["beneficiary"])
    restart = probe.run("R06_restart", output, config, "inspect")
    original_by_key = {row["request_key"]: row for row in original["decisions"]}
    probe.check("recovery_selected_original_v2", inspected.get("selected_state") == "state/control/history.sqlite"
                and inspected.get("result", {}).get("active_policy") == "BR-001/v2")
    probe.check("recovery_keeps_exact_old_and_current_records",
                old.get("result", {}).get("status") == current.get("result", {}).get("status") == "REPLAYED"
                and response_record(old).get("decision_id") == original_by_key[scenario["history_key"]]["decision_id"]
                and response_record(current).get("decision_id") == original_by_key[scenario["current_key"]]["decision_id"]
                and route(old) == "STANDARD_QUEUE" and route(current) == "HUMAN_REVIEW")
    probe.check("recovery_historical_recompute", recompute.get("result", {}).get("status") == "MATCH"
                and recompute.get("result", {}).get("recorded_policy") == "BR-001/v1")
    probe.check("recovery_survives_process_restart", restart.get("result", {}).get("active_policy") == "BR-001/v2"
                and restart.get("pid") != inspected.get("pid"))
    probe.check("recovered_original_bytes_and_incident_bytes_preserved",
                snapshot(output / "state/control/history.sqlite") == original
                and snapshot(output / "state/incident/history.sqlite") == incident)
    # Guard and fresh-write probes operate on separate NEW copies, never originals.
    missing = new_workspace(output / "probes/missing", root)
    probe.run("G01_missing_state", missing, config, "inspect", expected_error="STATE_MISSING_INITIALIZATION_FORBIDDEN")
    probe.check("missing_state_probe_creates_no_database", not list(missing.rglob("*.sqlite")))
    wrong = new_workspace(output / "probes/wrong_policy", root)
    for relative in STATE_PATHS:
        target = wrong / relative
        target.parent.mkdir(parents=True)
        shutil.copyfile(Path(session) / "state/incident/history.sqlite", target)
    wrong_before = tree_hashes(wrong)
    probe.run("G02_wrong_active_policy", wrong, config, "inspect", expected_error="ACTIVE_POLICY_BINDING_MISMATCH")
    probe.check("wrong_policy_guard_preserves_state", tree_hashes(wrong) == wrong_before)
    anchor = new_workspace(output / "probes/missing_anchor", root)
    for relative in STATE_PATHS:
        target = anchor / relative
        target.parent.mkdir(parents=True)
        shutil.copyfile(Path(session) / "state/incident/history.sqlite", target)
    probe.run("G03a_prepare_anchor_probe", anchor, root / CONTROL_CONFIG, "activate", policy="BR-001/v2")
    anchor_before = tree_hashes(anchor)
    probe.run("G03_missing_anchor", anchor, config, "inspect", expected_error="HISTORICAL_ANCHOR_MISSING")
    probe.check("missing_anchor_guard_preserves_state", tree_hashes(anchor) == anchor_before)
    smoke = new_workspace(output / "probes/new_request", root)
    shutil.copytree(Path(session) / "state", smoke / "state")
    fresh = probe.run("R07_new_request_on_probe_copy", smoke, config, "decide", key="recovery_probe_4000", **payload)
    probe.check("fresh_recovery_request_uses_v2", fresh.get("result", {}).get("status") == "CREATED"
                and route(fresh) == "HUMAN_REVIEW" and response_record(fresh).get("policy_version") == "BR-001/v2")
    return probe


def evaluate_incident(rehearsal, root=ROOT, reference=False, unsafe=False, output=None, receipt=None, scope_baseline=None):
    root = Path(root).resolve()
    if output is None:
        with tempfile.TemporaryDirectory(prefix="cp12-review-") as directory:
            return evaluate_incident(rehearsal, root, reference, unsafe, Path(directory) / "evidence", receipt, scope_baseline)
    target = safe_owned_path(output, root)
    rehearsal = safe_owned_path(rehearsal, root)
    if target.is_relative_to(rehearsal) or (receipt and target.is_relative_to(Path(receipt).absolute().parent)):
        raise ValueError("OUTPUT_MUST_NOT_NEST_IN_PRIOR_EVIDENCE")
    output = new_workspace(target, root)
    config, review = selected_paths(root, reference, unsafe)
    mode = "PROTECTED_REFERENCE" if reference else ("PROTECTED_UNSAFE_CONTROL" if unsafe else "WORKING_CANDIDATES")
    result = {"schema": "cp12-incident-review/v1", "status": "FAIL", "mode": mode,
              "rehearsal_mode": "NOT_READ", "findings": [], "checks": [],
              "edit_scope_checked": scope_baseline is not None,
              "restoration_status": "NOT_VALIDATED", "reconciliation_status": "QUARANTINED_PENDING_OWNER_RECONCILIATION",
              "permanent_fix_status": "NOT_VALIDATED", "python_version": sys.version.split()[0],
              "authority": {"CP07_T07_03": "PENDING_HUMAN", "CP07_T07_04": "BLOCKED", "payment_authorized": False,
                            "real_human_acceptance": False, "real_release_authorized": False,
                            "production_recovery_authorized": False, "incident_closed": False},
              "meaning": "Observed local state-selection recovery and guard checks. Both ledgers retained; no automatic reconciliation, production recovery, rollout or incident closure."}
    issues = result["findings"]
    try:
        issues.extend("PROTECTED_INTEGRITY:" + name for name in check_integrity(root))
        if scope_baseline:
            issues.extend(check_edit_scope(scope_baseline, root=root, chapter="CP12"))
        selected_reference = reference or unsafe
        inputs = session_inputs(root, selected_reference)
        inputs.update({config.relative_to(root).as_posix(): digest(config), review.relative_to(root).as_posix(): digest(review)})
        result["input_receipts"] = inputs
        if not issues:
            session, session_issues, checks = validate_session(rehearsal, root, selected_reference)
            issues.extend(session_issues)
            result["checks"].extend(checks)
            result["rehearsal_mode"] = session.get("mode", "INVALID") if isinstance(session, dict) else "INVALID"
            result["session_sha256"] = digest(Path(rehearsal) / "INCIDENT_SESSION.json")
            if receipt:
                issues.extend(receipt_findings(receipt, inputs, result["session_sha256"], mode))
        if not issues:
            before = tree_hashes(rehearsal)
            config_value = known_config(config, root)
            expected = read_json(root / REFERENCE_CONFIG)
            issues.extend("DEPLOYMENT:" + field for field in expected if config_value.get(field) != expected[field])
            issues.extend(review_findings(read_json(review), root))
            probe = recovery_probe(root, history_source(root, selected_reference), config, rehearsal, output)
            result["checks"].extend(probe.checks)
            issues.extend("RECOVERY:" + item["name"] for item in probe.checks if not item["passed"])
            original_preserved = tree_hashes(rehearsal) == before
            result["rehearsal_originals_unchanged"] = original_preserved
            if not original_preserved:
                issues.append("REHEARSAL_ORIGINALS_CHANGED")
            restoration = [item for item in probe.checks if item["name"].startswith(("R", "recovery_", "recovered_", "fresh_recovery_"))]
            guards = [item for item in probe.checks if item["name"].startswith(("G", "missing_", "wrong_"))]
            if restoration and all(item["passed"] for item in restoration):
                result["restoration_status"] = "VALIDATED_LOCAL_SELECTION"
            if guards and all(item["passed"] for item in guards):
                result["permanent_fix_status"] = "LOCAL_GUARD_VALIDATED_NO_PRODUCTION_ROLLOUT"
        if check_integrity(root):
            issues.append("PROTECTED_INTEGRITY_CHANGED_DURING_CHECKS")
        if result.get("input_receipts") and any(digest(root / name) != value for name, value in inputs.items()):
            issues.append("SOURCE_CHANGED_DURING_CHECKS")
    except (OSError, ValueError, TypeError, AttributeError, KeyError, sqlite3.Error, subprocess.SubprocessError) as exc:
        issues.append("INCIDENT_ERROR:" + type(exc).__name__ + ":" + str(exc))
    result["evidence_sha256"] = tree_hashes(output)
    result["status"] = SUCCESS if not issues and result["checks"] else "FAIL"
    write_json(output / "INCIDENT_RESULT.json", result)
    return result
