"""Inspect selected ledger state without creating, changing
or merging ledgers.
"""
from pathlib import Path
from contextlib import closing
import hashlib
import json
import sqlite3
from operations import cost_summary

APPLICATION_ID = 1129337137


def inspect_ledger(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError("ledger is missing; diagnosis cannot initialize it")
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as con:
        if con.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID:
            raise ValueError("wrong application database")
        if con.execute("PRAGMA user_version").fetchone()[0] != 2:
            raise ValueError("unsupported schema")
        policy = con.execute("SELECT value FROM settings WHERE name='active_policy'").fetchone()[0]
        rows = con.execute("""
            SELECT request_key , decision_id , policy_version ,
            decision_json FROM decisions ORDER BY request_key
        """).fetchall()
        audit_count = con.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0]
    after = hashlib.sha256(path.read_bytes()).hexdigest()
    if before != after:
        raise RuntimeError("ledger changed during observation")
    return {"path":str(path), "sha256":before, "schema_version":2, "active_policy":policy,
            "decisions":[{"request_id":r[0],"decision_id":r[1],"policy_version":r[2],"decision":json.loads(r[3])} for r in rows],
            "audit_count":audit_count,"unchanged":True}


def diagnose(
    selected_path, expected_path, *, expected_policy, anchor_key
):
    selected, expected = (
        inspect_ledger(expected_path), inspect_ledger(expected_path))
    issues = []
    if selected["path"] != expected["path"]:
        issues.append("STATE_PATH_MISMATCH")
    if selected["active_policy"] != expected_policy:
        issues.append("ACTIVE_POLICY_MISMATCH")
    if anchor_key not in {
        r["request_id"] for r in selected["decisions"]
    }:
        issues.append("ANCHOR_MISSING")
    return {
        "status": (
            "WRONG_LEDGER" if issues else "EXPECTED_LEDGER_SELECTED"),
        "issues": issues, "selected": selected, "expected": expected,
        "restoration": "NOT_PERFORMED",
        "reconciliation": "PENDING_OWNER_DECISION"}


def recovery_plan(diagnosis):
    return {
        "restore_configuration_to": diagnosis["expected"]["path"],
        "preserve_ledgers": [
            diagnosis["selected"]["path"],
            diagnosis["expected"]["path"]],
        "verification": [
            "historical replay",
            "current-policy decision on disposable copy",
            "restart and state binding"],
        "automatic_merge": False,
        "reconciliation": "PENDING_OWNER_DECISION",
        "production_authorized": False}
