"""Read-only wrong-ledger diagnosis and recovery planning (OPS-B4/v2).

Nothing here writes to, initializes, merges or restores a ledger.
"""
from contextlib import closing
from pathlib import Path
import hashlib
import sqlite3

import ledger
from operations import cost_summary  # noqa: F401  (G4 accepted-outcome accounting, re-exported)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_ledger(path):
    """Observe an existing HISTORY schema 2 ledger without creating or changing it."""
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(str(path))  # never create a missing path
    before = _sha(path)
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        if con.execute("PRAGMA application_id").fetchone()[0] != ledger.APPLICATION_ID:
            raise ledger.HistoryError("WRONG_DATABASE")
        if con.execute("PRAGMA user_version").fetchone()[0] != ledger.SCHEMA_VERSION:
            raise ledger.HistoryError("UNSUPPORTED_SCHEMA")
        row = con.execute("SELECT value FROM settings WHERE name='active_policy'").fetchone()
        if row is None:
            raise ledger.HistoryError("ACTIVE_POLICY_MISSING")
        decisions = [
            {"request_id": r["request_key"], "decision_id": r["decision_id"],
             "policy_version": r["policy_version"], "parent_key": r["parent_key"]}
            for r in con.execute(
                "SELECT request_key,decision_id,policy_version,parent_key "
                "FROM decisions ORDER BY request_key")]
        audit_count = con.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0]
        active = row[0]
    if _sha(path) != before:
        raise RuntimeError("ledger changed during read-only inspection")
    return {"path": str(path), "digest": before, "active_policy": active,
            "decisions": decisions, "audit_count": audit_count}


def diagnose(selected_path, expected_path, *, expected_policy, anchor_key):
    """Compare selected state with the expected ledger; state, not source code, is judged."""
    selected = inspect_ledger(selected_path)
    expected = inspect_ledger(expected_path)
    issues = []
    if selected["path"] != expected["path"]:
        issues.append("STATE_PATH_MISMATCH")
    if selected["active_policy"] != expected_policy:
        issues.append("ACTIVE_POLICY_MISMATCH")
    if anchor_key not in {d["request_id"] for d in selected["decisions"]}:
        issues.append("ANCHOR_MISSING")
    return {
        "status": "WRONG_LEDGER" if issues else "EXPECTED_LEDGER_SELECTED",
        "issues": issues,
        "selected": selected,
        "expected": expected,
        "expected_policy": expected_policy,
        "anchor_key": anchor_key,
        "source_regression_established": False,
        "lineage_note": "Equal deterministic decision IDs across ledgers do not establish replay lineage.",
        "ledgers_unchanged": True,
    }


def recovery_plan(diagnosis):
    """Propose (never perform or authorize) restoring the expected state binding."""
    sel, exp = diagnosis["selected"]["path"], diagnosis["expected"]["path"]
    return {
        "status": "PROPOSAL_ONLY",
        "diagnosis_status": diagnosis["status"],
        "restore_configuration_to": exp,
        "preserve_ledgers": [exp] if sel == exp else [exp, sel],
        "automatic_merge": False,
        "production_authorized": False,
        "restoration": {"proposed": diagnosis["status"] == "WRONG_LEDGER",
                        "performed": False,
                        "owner": "operator (separate local fixture change)"},
        "reconciliation": "PENDING_OWNER_DECISION",
        "reconciliation_note": ("Records created while the wrong state was selected need the owner, "
                                "conflict analysis and separate evidence; no rows are merged."),
        "next_checks": [
            "historical replay of recorded decisions against the expected ledger",
            "new-current-policy probe on a disposable copy only",
            "restart/state check after the operator restores the binding",
        ],
    }
