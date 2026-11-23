"""Read-only diagnostics and an explicit account of
accepted-outcome cost.
"""
from pathlib import Path
from decimal import Decimal, InvalidOperation
from contextlib import closing
import hashlib
import sqlite3


def diagnose(path):
    path = Path(path).resolve()
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    # OPS-G4/v3: (table, complete signature, identifier column).
    signatures = [
        ("reservations", ("id", "asset_id", "member_id", "starts_at", "ends_at", "request_key", "request_hash", "state", "version"), "id"),
        ("reservations_v2", ("reservation_id", "trusted_member_id", "asset_id", "starts_at", "ends_at", "idempotency_key", "payload_fingerprint", "state", "version"), "reservation_id"),
        ("reservations_v2", ("id", "trusted_member_id", "asset_id", "starts_at", "ends_at", "idempotency_key", "fingerprint", "state", "version"), "id"),
    ]
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as con:
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version != 3:
            raise ValueError("G4 requires the identified G3 schema")
        matches = [(name, key) for name, signature, key in signatures
                   if tuple(row[1] for row in con.execute("PRAGMA table_info(" + name + ")")) == signature]
        if len(matches) != 1:
            raise ValueError("Unsupported or competing current representations")
        table, key = matches[0]
        rows = con.execute("SELECT state,COUNT(*) FROM " + table + " GROUP BY state").fetchall()
        overlaps = con.execute(
            f"SELECT a.{key},b.{key} FROM {table} a JOIN {table} b "
            f"ON a.{key}<b.{key} AND a.asset_id=b.asset_id "
            "AND a.starts_at<b.ends_at AND b.starts_at<a.ends_at "
            f"WHERE a.state='active' AND b.state='active' ORDER BY a.{key},b.{key}"
        ).fetchall()
    after = hashlib.sha256(path.read_bytes()).hexdigest()
    if before != after:
        raise RuntimeError("database changed during diagnostic observation")
    return {"database": str(path), "schema_version": version, "counts": dict(rows),
            "active_overlap_pairs": [list(x) for x in overlaps],
            "database_sha256": before, "unchanged": True,
            "diagnosis": "ACTIVE_OVERLAP" if overlaps else "NO_ACTIVE_OVERLAP_OBSERVED"}


def _billable_attempts(attempts):
    return [a for a in attempts if a.get("status") != "FAILED"]


def cost_summary(attempts, accepted):
    attempts = _billable_attempts(attempts)
    if type(accepted) is not int or accepted < 0:
        raise ValueError("accepted must be a nonnegative count")
    money = Decimal("0")
    minutes = Decimal("0")
    for a in attempts:
        try:
            cost = Decimal(str(a["cost_eur"]))
            duration = Decimal(str(a["minutes"]))
        except InvalidOperation as error:
            raise ValueError(
                "cost and time must be decimal numbers"
            ) from error
        if (not cost.is_finite() or not duration.is_finite()
                or cost < 0 or duration < 0):
            raise ValueError(
                "cost and time must be finite and nonnegative"
            )
        money += cost
        minutes += duration
    return {
        "attempts": len(attempts),
        "accepted_outcomes": accepted,
        "total_cost_eur": str(money),
        "total_minutes": str(minutes),
        "cost_per_accepted_eur": (
            None if accepted == 0 else str(money / accepted)),
        "minutes_per_accepted": (
            None if accepted == 0 else str(minutes / accepted)),
        "status": (
            "NO_ACCEPTED_OUTCOME" if accepted == 0 else "ACCOUNTED")}
