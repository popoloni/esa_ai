"""B4 wrong-ledger diagnosis and recovery planning (OPS-B4/v2). Read-only; no production authority."""
from contextlib import closing
from hashlib import sha256
from pathlib import Path
import sqlite3

from ledger import APPLICATION_ID, SCHEMA_VERSION, HistoryError
from operations import cost_summary  # G4 accepted-outcome accounting, incl. failed attempts

__all__ = ["inspect_ledger", "diagnose", "recovery_plan", "cost_summary"]


def inspect_ledger(path):
    """Observe an existing HISTORY schema 2 ledger read-only; never create it."""
    resolved = Path(path).resolve()
    if not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    before = sha256(resolved.read_bytes()).hexdigest()
    with closing(sqlite3.connect(resolved.as_uri() + "?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        if con.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID:
            raise HistoryError("WRONG_DATABASE")
        if con.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
            raise HistoryError("UNSUPPORTED_SCHEMA")
        row = con.execute("SELECT value FROM settings WHERE name='active_policy'").fetchone()
        decisions = [
            {"request_id": r["request_key"], "decision_id": r["decision_id"],
             "policy_version": r["policy_version"], "parent_key": r["parent_key"]}
            for r in con.execute(
                "SELECT request_key,decision_id,policy_version,parent_key "
                "FROM decisions ORDER BY request_key")]
        audit_count = con.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0]
    after = sha256(resolved.read_bytes()).hexdigest()
    if before != after:
        raise RuntimeError("ledger changed during observation")
    return {"path": str(resolved), "digest": before,
            "active_policy": None if row is None else row[0],
            "decisions": decisions, "audit_count": audit_count}


def diagnose(selected_path, expected_path, *, expected_policy, anchor_key):
    """Compare selected state with expected state; same code can route differently."""
    selected = inspect_ledger(selected_path)
    expected = inspect_ledger(expected_path)
    issues = []
    if selected["path"] != expected["path"]:
        issues.append("STATE_PATH_MISMATCH")
    if selected["active_policy"] != expected_policy:
        issues.append("ACTIVE_POLICY_MISMATCH")
    if anchor_key not in {d["request_id"] for d in selected["decisions"]}:
        issues.append("ANCHOR_MISSING")
    # Equal decision IDs across different paths are not evidence of shared lineage.
    shared = sorted({d["decision_id"] for d in selected["decisions"]}
                    & {d["decision_id"] for d in expected["decisions"]})
    return {"status": "WRONG_LEDGER" if issues else "EXPECTED_LEDGER_SELECTED",
            "issues": issues, "selected": selected, "expected": expected,
            "expected_policy": expected_policy, "anchor_key": anchor_key,
            "shared_decision_ids": shared,
            "lineage_established": False,
            "lineage_note": "Deterministic decision IDs alone do not establish replay lineage.",
            "ledgers_unchanged": True}


def recovery_plan(diagnosis):
    """Structured proposal only: restoring a binding is not merging or authorization."""
    sel, exp = diagnosis["selected"]["path"], diagnosis["expected"]["path"]
    return {
        "restore_configuration_to": exp,
        "restore_state_binding_to": exp,  # compatibility alias
        "restoration_needed": diagnosis["status"] != "EXPECTED_LEDGER_SELECTED",
        "automatic_merge": False,
        "production_authorized": False,
        "preserve_ledgers": sorted({sel, exp}),
        "reconciliation": "PENDING_OWNER_DECISION",
        "reconciliation_note": (
            "Records created while the wrong state was selected need the owner, conflict "
            "analysis and separate evidence; this plan does not decide them."),
        "steps": ["restore the expected state binding (separate operator change)",
                  "historical replay of recorded decisions with recorded policy snapshots",
                  "new-current-policy probe on a disposable copy only",
                  "restart and state checks"],
        "issues": list(diagnosis["issues"]),
        "next_authorized_check": "operator-run restart/state check after the binding is restored",
    }
