"""Owner-side checks for known CP11 code and persistent synthetic history."""
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import subprocess
import sys
import tempfile

from scope_guard import check_integrity, check_edit_scope, check_candidate_path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = "repo/src/treasury/policy_history.py"
DELTA = "repo/engineering/evolution/policy_delta.json"
REFERENCE = "reader_side/reference_solution/ch11/policy_history.py"
REFERENCE_DELTA = "reader_side/reference_solution/ch11/policy_delta.json"
UNSAFE = "reader_side/evolution/unsafe_policy_history.py"
UNSAFE_DELTA = "reader_side/evolution/unsafe_policy_delta.json"
SUCCESS = "PASS_POLICY_EVOLUTION_REVIEW_ONLY"
APPLICATION_ID = 1129337137
OWNER_INPUTS = [
    "reader_side/evolution/policy_catalog.json", "reader_side/evolution/case_oracle.json",
    "reader_side/evolution/legacy_complete.json", "reader_side/evolution/legacy_ambiguous.json",
    "reader_side/evolution/legacy_wrong_outcome.json", "reader_side/evolution/WORK_ORDER_CP11.md",
    "reader_side/evolution/change_context.json", "reader_side/discovery/sources/SRC-POL-001.json",
    "repo/src/treasury/routing.py", "reader_side/protected_sha256.json",
]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def environment():
    result = dict(os.environ)
    result.pop("PYTHONPATH", None)
    result["PYTHONDONTWRITEBYTECODE"] = "1"
    return result


def selected_paths(root, reference=False, unsafe=False):
    if reference and unsafe:
        raise ValueError("Choose only one fixture mode")
    names = (UNSAFE, UNSAFE_DELTA) if unsafe else ((REFERENCE, REFERENCE_DELTA) if reference else (CANDIDATE, DELTA))
    return tuple(Path(root) / name for name in names)


def load_candidate(path, root=ROOT):
    root, path = Path(root).resolve(), Path(path).resolve()
    if path not in {root / name for name in (CANDIDATE, REFERENCE, UNSAFE)}:
        raise ValueError("CANDIDATE_PATH_NOT_ALLOWED")
    if path == root / CANDIDATE:
        check_candidate_path(CANDIDATE.removeprefix("repo/"), repo=root / "repo", chapter="CP11")
    sys.path.insert(0, str(root / "repo/src"))
    spec = importlib.util.spec_from_file_location("known_cp11_candidate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def catalog(root=ROOT):
    return read_json(Path(root) / "reader_side/evolution/policy_catalog.json")["policies"]


def safe_database_path(path, root=ROOT):
    path, root = Path(path), Path(root).resolve()
    if path.is_symlink():
        raise ValueError("DATABASE_SYMLINK")
    resolved = path.resolve()
    if resolved.is_relative_to(root) and not resolved.is_relative_to(root / "reader_side/evidence"):
        raise ValueError("DATABASE_MUST_BE_OUTSIDE_SOURCE")
    return resolved


def operate(path, database, operation, arguments, root=ROOT):
    """Run one operation; the CLI invokes this in a fresh process each time."""
    policies = catalog(root)
    database = safe_database_path(database, root)
    if operation == "migrate":
        provenance = checked_provenance(database, arguments["provenance"], root)
        module = load_candidate(path, root)
        return module.migrate_legacy(database, policies, provenance)
    module = load_candidate(path, root)
    if operation == "init" and database.exists():
        raise ValueError("DATABASE_ALREADY_EXISTS")
    if operation != "init" and not database.is_file():
        raise ValueError("DATABASE_MISSING")
    store = module.PolicyStore(database, policies)
    try:
        if operation == "init":
            return {"status": "INITIALIZED", "active_policy": store.active_policy()}
        if operation == "activate":
            return store.activate(arguments["policy"])
        if operation == "decide":
            return store.decide(arguments["key"], {"amount_eur": arguments["amount"],
                                "beneficiary_id": arguments["beneficiary"]}, arguments.get("policy"))
        if operation == "replay":
            return store.replay(arguments["key"])
        if operation == "recompute":
            return store.recompute(arguments["key"])
        if operation == "reevaluate":
            return store.reevaluate(arguments["from_key"], arguments["key"], arguments["policy"])
        raise ValueError("UNKNOWN_OPERATION")
    finally:
        store.close()


def seed_legacy(output, fixture="complete", root=ROOT):
    """Create a NEW explicitly synthetic v1 database and owner provenance."""
    if fixture not in {"complete", "ambiguous", "wrong_outcome"}:
        raise ValueError("UNKNOWN_LEGACY_FIXTURE")
    output = safe_database_path(output, root)
    output.mkdir(parents=True, exist_ok=False)
    data = read_json(Path(root) / ("reader_side/evolution/legacy_" + fixture + ".json"))
    rows = sorted(data["rows"], key=lambda row: row["request_key"])
    path = output / "history.sqlite"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE legacy_decisions(request_key TEXT PRIMARY KEY, payload_json TEXT, policy_json TEXT, decision_json TEXT)")
        for row in rows:
            conn.execute("INSERT INTO legacy_decisions VALUES(?,?,?,?)",
                         tuple(row[key] for key in ("request_key", "payload_json", "policy_json", "decision_json")))
        conn.execute(f"PRAGMA application_id={APPLICATION_ID}")
        conn.execute("PRAGMA user_version=1")
    provenance = {"schema": "cp11-legacy-provenance/v1", "origin": data["origin"],
                  "source_id": data["source_id"], "rows_sha256": sha256(canonical(rows).encode()).hexdigest()}
    write_json(output / "provenance.json", provenance)
    return {"status": "SEEDED_SYNTHETIC_LEGACY", "database": str(path),
            "provenance": str(output / "provenance.json"), "source_id": data["source_id"]}


def database_rows(path, table="decisions"):
    if table not in {"decisions", "audit_events", "legacy_decisions"}:
        raise ValueError("Unknown inspection table")
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        order = "event_id" if table == "audit_events" else "request_key"
        return [dict(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY {order}")]


def checked_provenance(database, supplied_path, root=ROOT):
    """Bind claimed provenance to protected synthetic evidence, not self-claims."""
    supplied = read_json(supplied_path)
    expected = {}
    for name in ("complete", "ambiguous", "wrong_outcome"):
        fixture = read_json(Path(root) / ("reader_side/evolution/legacy_" + name + ".json"))
        rows = sorted(fixture["rows"], key=lambda row: row["request_key"])
        expected[fixture["source_id"]] = sha256(canonical(rows).encode()).hexdigest()
    source_id = supplied.get("source_id") if isinstance(supplied, dict) else None
    if (not isinstance(source_id, str) or source_id not in expected
            or supplied.get("schema") != "cp11-legacy-provenance/v1"
            or supplied.get("origin") != "SYNTHETIC_BROWNFIELD_FIXTURE"
            or supplied.get("rows_sha256") != expected[source_id]
            or sha256(canonical(database_rows(database, "legacy_decisions")).encode()).hexdigest() != expected[source_id]):
        raise ValueError("LEGACY_PROVENANCE_NOT_OWNER_BOUND")
    return supplied


def check_receipt(path, inputs, mode):
    issues = []
    try:
        path = Path(path).resolve()
        prior = read_json(path)
        if not isinstance(prior, dict) or prior.get("schema") != "cp11-evolution-review/v1":
            return ["RECEIPT_SCHEMA"]
        if prior.get("status") != SUCCESS or prior.get("mode") != mode:
            issues.append("RECEIPT_STATUS_OR_MODE")
        old = prior.get("input_receipts")
        if not isinstance(old, dict):
            return issues + ["RECEIPT_INPUTS_MISSING"]
        for name in sorted(set(old) | set(inputs)):
            if old.get(name) != inputs.get(name):
                issues.append("STALE_RECEIPT:" + name)
        artifacts = prior.get("evidence_sha256")
        if not isinstance(artifacts, dict) or not artifacts:
            return issues + ["RECEIPT_EVIDENCE_MISSING"]
        for name, expected in artifacts.items():
            relative = PurePosixPath(name)
            if relative.is_absolute() or ".." in relative.parts or str(relative) != name:
                issues.append("RECEIPT_EVIDENCE_PATH")
                continue
            item = path.parent / name
            if item.is_symlink() or not item.is_file() or digest(item) != expected:
                issues.append("STALE_EVIDENCE:" + name)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        issues.append("RECEIPT_UNREADABLE:" + type(exc).__name__)
    return issues


def delta_findings(supplied, root=ROOT):
    expected = read_json(Path(root) / REFERENCE_DELTA)
    if not isinstance(supplied, dict):
        return ["DELTA_SCHEMA"]
    findings = ["POLICY_DELTA:" + key for key in expected if supplied.get(key) != expected[key]]
    if set(supplied) != set(expected):
        findings.append("POLICY_DELTA:fields")
    claims = supplied.get("claims")
    if (not isinstance(claims, dict) or set(claims) != set(expected["claims"])
            or any(value is not False for value in claims.values())):
        findings.append("POLICY_DELTA:authority_claims")
    return findings


class Probe:
    def __init__(self, root, candidate, output):
        self.root, self.candidate, self.output = Path(root), Path(candidate), Path(output)
        self.checks, self.steps = [], []

    def command(self, database, operation, values):
        command = [sys.executable, "-B", str(self.root / "reader_side/tools/policy_history_cli.py"),
                   "--db", str(database), "--candidate", str(self.candidate), operation]
        for name, value in values.items():
            command += ["--" + name.replace("_", "-"), str(value)]
        return command

    def check(self, name, condition, detail=None):
        self.checks.append({"name": name, "passed": bool(condition), "observed": detail})

    def collect(self, name, completed, expected_error=None):
        try:
            data = json.loads(completed.stdout)
        except ValueError:
            data = {"status": "FAIL", "error": "INVALID_WORKER_OUTPUT"}
        write_json(self.output / "steps" / (name + ".json"), data)
        (self.output / "steps" / (name + ".log")).write_text(completed.stdout + "\nSTDERR\n" + completed.stderr)
        expected_exit = 1 if expected_error else 0
        self.check(name + "_execution", completed.returncode == expected_exit
                   and (data.get("error") == expected_error if expected_error else data.get("status") == "OK"), data)
        self.steps.append({"name": name, "returncode": completed.returncode, "error": data.get("error")})
        return data.get("result", {})

    def run(self, name, database, operation, expected_error=None, **values):
        completed = subprocess.run(self.command(database, operation, values), cwd=self.root,
                                   env=environment(), capture_output=True, text=True, timeout=30)
        return self.collect(name, completed, expected_error)


def exercise(root, candidate, output):
    """Fresh processes share actual SQLite files; owner assertions read them."""
    probe = Probe(root, candidate, output)
    oracle = read_json(Path(root) / "reader_side/evolution/case_oracle.json")
    db = output / "history.sqlite"
    probe.run("initialize", db, "init")
    original = probe.run("original_v1", db, "decide", key="original_4000", amount="4000.00", beneficiary="vendor_17")
    original_record = original.get("record", {})
    probe.check("original_v1_route", original_record.get("decision", {}).get("route") == "STANDARD_QUEUE", original_record)
    before = database_rows(db)
    probe.run("activate_v2", db, "activate", policy="BR-001/v2")
    events_after_activation = database_rows(db, "audit_events")
    replay = probe.run("stored_replay_after_restart", db, "replay", key="original_4000")
    probe.check("stored_response_unchanged", replay == original_record, replay)
    historical = probe.run("historical_recompute_after_restart", db, "recompute", key="original_4000")
    probe.check("historical_policy_recomputed", historical.get("status") == "MATCH"
                and historical.get("recorded_policy") == "BR-001/v1"
                and historical.get("recomputed", {}).get("route") == "STANDARD_QUEUE", historical)
    retry = probe.run("retry_after_rollout", db, "decide", key="original_4000", amount="4000.0", beneficiary="vendor_17")
    probe.check("canonical_retry_same_identity", retry.get("status") == "REPLAYED" and retry.get("record") == original_record, retry)
    probe.check("read_and_retry_do_not_append", database_rows(db) == before
                and database_rows(db, "audit_events") == events_after_activation)
    probe.run("changed_amount_conflict", db, "decide", expected_error="IDEMPOTENCY_CONFLICT",
              key="original_4000", amount="4001", beneficiary="vendor_17")
    probe.run("changed_beneficiary_conflict", db, "decide", expected_error="IDEMPOTENCY_CONFLICT",
              key="original_4000", amount="4000", beneficiary="vendor_18")
    probe.run("explicit_policy_change_conflict", db, "decide", expected_error="IDEMPOTENCY_CONFLICT",
              key="original_4000", amount="4000", beneficiary="vendor_17", policy="BR-001/v2")
    probe.run("explicit_unknown_retry_policy", db, "decide", expected_error="UNKNOWN_POLICY",
              key="original_4000", amount="4000", beneficiary="vendor_17", policy="BR-001/v999")
    probe.run("same_key_reevaluation_blocked", db, "reevaluate", expected_error="NEW_KEY_REQUIRED",
              from_key="original_4000", key="original_4000", policy="BR-001/v2")
    newer = probe.run("deliberate_reevaluation", db, "reevaluate",
                      from_key="original_4000", key="reevaluated_4000", policy="BR-001/v2")
    new_record = newer.get("record", {})
    probe.check("new_identity_linked_to_original", new_record.get("parent_key") == "original_4000"
                and new_record.get("decision_id") != original_record.get("decision_id")
                and new_record.get("policy_version") == "BR-001/v2"
                and new_record.get("decision", {}).get("route") == "HUMAN_REVIEW", newer)
    again = probe.run("reevaluation_retry", db, "reevaluate",
                      from_key="original_4000", key="reevaluated_4000", policy="BR-001/v2")
    probe.check("reevaluation_retry_same_record", again.get("status") == "REPLAYED" and again.get("record") == new_record)
    probe.run("reevaluation_policy_conflict", db, "reevaluate", expected_error="IDEMPOTENCY_CONFLICT",
              from_key="original_4000", key="reevaluated_4000", policy="BR-001/v1")
    probe.run("parent_operation_conflict", db, "decide", expected_error="IDEMPOTENCY_CONFLICT",
              key="reevaluated_4000", amount="4000", beneficiary="vendor_17")
    for case in oracle["cases"]:
        result = probe.run("boundary_" + case["id"], db, "decide", key=case["id"],
                           amount=case["amount"], beneficiary="boundary", policy=case["policy"])
        decision = result.get("record", {}).get("decision", {})
        probe.check("oracle_" + case["id"], decision.get("route") == case["route"]
                    and decision.get("reason_code") == case["reason"]
                    and decision.get("policy_version") == case["policy"]
                    and decision.get("payment_authorized") is False, decision)
    for index, amount in enumerate(oracle["invalid_amounts"]):
        probe.run("invalid_format_" + str(index), db, "decide", expected_error="INVALID_AMOUNT_FORMAT",
                  key="bad_format_" + str(index), amount=amount, beneficiary="boundary")
    probe.run("unknown_policy", db, "activate", expected_error="UNKNOWN_POLICY", policy="BR-001/v999")
    # Real competing connections: hold the write lock, start both writers, release.
    race = output / "race.sqlite"
    probe.run("race_initialize", race, "init")
    lock = sqlite3.connect(race, isolation_level=None)
    lock.execute("BEGIN IMMEDIATE")
    processes = [subprocess.Popen(probe.command(race, "decide", {"key": "race_key", "amount": amount, "beneficiary": "race"}),
                                  cwd=root, env=environment(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                 for amount in ("4000", "4001")]
    lock.commit()
    lock.close()
    race_outputs = []
    for index, process in enumerate(processes):
        stdout, stderr = process.communicate(timeout=30)
        data = json.loads(stdout)
        expected = "IDEMPOTENCY_CONFLICT" if data.get("error") == "IDEMPOTENCY_CONFLICT" else None
        probe.collect("race_writer_" + str(index), subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr), expected)
        race_outputs.append(data)
    probe.check("two_process_race_single_winner", sum(item.get("status") == "OK" for item in race_outputs) == 1
                and sum(item.get("error") == "IDEMPOTENCY_CONFLICT" for item in race_outputs) == 1
                and len(database_rows(race)) == len(database_rows(race, "audit_events")) == 1, race_outputs)
    # A real SQLite trigger aborts the second insert, after the decision insert.
    with sqlite3.connect(db) as connection:
        connection.execute("""CREATE TRIGGER owner_injected_audit_failure BEFORE INSERT ON audit_events
          WHEN NEW.event_type='DECISION_RECORDED' AND NEW.request_key='atomic_failure'
          BEGIN SELECT RAISE(ABORT,'owner_injected_audit_failure'); END""")
    before_failure, events_before = database_rows(db), database_rows(db, "audit_events")
    probe.run("audit_failure", db, "decide", expected_error="SQLITE_INTEGRITY",
              key="atomic_failure", amount="100", beneficiary="atomic")
    probe.check("decision_and_audit_atomic", database_rows(db) == before_failure
                and database_rows(db, "audit_events") == events_before)
    with sqlite3.connect(db) as connection:
        connection.execute("DROP TRIGGER owner_injected_audit_failure")
    recovered = probe.run("retry_after_rollback", db, "decide", key="atomic_failure", amount="100", beneficiary="atomic")
    probe.check("failed_attempt_left_no_claim", recovered.get("status") == "CREATED")
    for fixture, error in (("complete", None), ("ambiguous", "HISTORY_AMBIGUOUS"),
                           ("wrong_outcome", "LEGACY_OUTCOME_MISMATCH")):
        directory = output / ("legacy_" + fixture)
        seeded = seed_legacy(directory, fixture, root)
        legacy = Path(seeded["database"])
        old_rows = database_rows(legacy, "legacy_decisions")
        old_hash = digest(legacy)
        result = probe.run("migration_" + fixture, legacy, "migrate", expected_error=error,
                           provenance=seeded["provenance"])
        probe.check("legacy_rows_preserved_" + fixture, database_rows(legacy, "legacy_decisions") == old_rows)
        if error:
            with sqlite3.connect(legacy) as connection:
                tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                version = connection.execute("PRAGMA user_version").fetchone()[0]
            probe.check("migration_atomic_abort_" + fixture, version == 1 and tables == {"legacy_decisions"} and digest(legacy) == old_hash)
        else:
            probe.check("migration_complete_count", result.get("status") == "MIGRATED" and result.get("records") == 1)
            probe.run("migrated_activate_v2", legacy, "activate", policy="BR-001/v2")
            result = probe.run("migrated_historical_recompute", legacy, "recompute", key="legacy_4000")
            probe.check("migrated_history_retains_v1", result.get("recorded_policy") == "BR-001/v1"
                        and result.get("recomputed", {}).get("route") == "STANDARD_QUEUE")
            probe.run("migration_not_repeated", legacy, "migrate", expected_error="LEGACY_SCHEMA_REQUIRED",
                      provenance=seeded["provenance"])
    seeded = seed_legacy(output / "legacy_forged_provenance", "complete", root)
    forged = read_json(seeded["provenance"])
    forged["source_id"] = "INVENTED-BUT-SELF-CONSISTENT"
    write_json(seeded["provenance"], forged)
    original_hash = digest(seeded["database"])
    probe.run("invented_legacy_provenance", Path(seeded["database"]), "migrate",
              expected_error="LEGACY_PROVENANCE_NOT_OWNER_BOUND", provenance=seeded["provenance"])
    probe.check("forged_provenance_did_not_touch_history", digest(seeded["database"]) == original_hash)
    return probe


def evaluate_evolution(root=ROOT, reference=False, unsafe=False, output=None, receipt=None, scope_baseline=None):
    root = Path(root).resolve()
    if output is None:
        with tempfile.TemporaryDirectory(prefix="cp11-review-") as directory:
            return evaluate_evolution(root, reference, unsafe, Path(directory) / "evidence", receipt, scope_baseline)
    output = safe_database_path(output, root)
    output.mkdir(parents=True, exist_ok=False)
    candidate, delta = selected_paths(root, reference, unsafe)
    mode = "PROTECTED_REFERENCE" if reference else ("PROTECTED_UNSAFE_CONTROL" if unsafe else "WORKING_CANDIDATES")
    result = {"schema": "cp11-evolution-review/v1", "status": "FAIL", "mode": mode,
              "findings": [], "checks": [], "edit_scope_checked": scope_baseline is not None,
              "python_version": sys.version.split()[0], "sqlite_version": sqlite3.sqlite_version,
              "authority": {"CP07_T07_03": "PENDING_HUMAN", "CP07_T07_04": "BLOCKED",
                            "payment_authorized": False, "real_human_acceptance": False,
                            "real_release_authorized": False, "policy_evolution_release_authorized": False},
              "meaning": "Selected persistent history and migration checks for a synthetic teaching experiment. No production migration, live payment or release approval."}
    issues = result["findings"]
    try:
        issues.extend("PROTECTED_INTEGRITY:" + name for name in check_integrity(root))
        if scope_baseline:
            issues.extend(check_edit_scope(scope_baseline, root=root, chapter="CP11"))
        paths = [candidate, delta] + [root / name for name in OWNER_INPUTS]
        inputs = {path.relative_to(root).as_posix(): digest(path) for path in paths}
        result["input_receipts"] = inputs
        if receipt:
            issues.extend(check_receipt(receipt, inputs, mode))
        if not issues:
            issues.extend(delta_findings(read_json(delta), root))
            # Exercise behavior even when the learner's report is wrong.
            probe = exercise(root, candidate, output)
            result["checks"], result["steps"] = probe.checks, probe.steps
            issues.extend("BEHAVIOR:" + check["name"] for check in probe.checks if not check["passed"])
        if check_integrity(root):
            issues.append("PROTECTED_INTEGRITY_CHANGED_DURING_CHECKS")
        if result.get("input_receipts") and any(digest(root / name) != value for name, value in result["input_receipts"].items()):
            issues.append("SOURCE_CHANGED_DURING_CHECKS")
    except (OSError, ValueError, TypeError, AttributeError, KeyError, sqlite3.Error, subprocess.SubprocessError) as exc:
        issues.append("EVOLUTION_ERROR:" + type(exc).__name__ + ":" + str(exc))
    result["evidence_sha256"] = {path.relative_to(output).as_posix(): digest(path)
                                 for path in sorted(output.rglob("*")) if path.is_file()}
    result["status"] = SUCCESS if not issues and result["checks"] else "FAIL"
    write_json(output / "EVOLUTION_RESULT.json", result)
    return result
