"""G4 operations: read-only diagnosis and accepted-outcome cost accounting (OPS-G4/v2).

diagnose() targets only the two documented G3 schema-3 representations; it does not
certify arbitrary databases. It never repairs, deletes or initialises anything.
"""
import hashlib
import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

_REFERENCE = ("id", "asset_id", "member_id", "starts_at", "ends_at",
              "request_key", "request_hash", "state", "version")
_RECORDED = ("reservation_id", "trusted_member_id", "asset_id", "starts_at", "ends_at",
             "idempotency_key", "payload_fingerprint", "state", "version")
_REPRESENTATIONS = (("reservations", "id", _REFERENCE),
                    ("reservations_v2", "reservation_id", _RECORDED))


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def diagnose(path):
    p = Path(path).resolve()
    if not p.is_file():
        raise FileNotFoundError("storage not found: " + str(p))
    before = _digest(p)
    con = sqlite3.connect(p.as_uri() + "?mode=ro", uri=True)
    try:
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version != 3:
            raise ValueError("unsupported schema version %s; only schema 3 is supported" % version)
        matches = []
        for table, id_col, signature in _REPRESENTATIONS:
            cols = tuple(r[1] for r in con.execute("PRAGMA table_info(" + table + ")"))
            if cols == signature:
                matches.append((table, id_col))
        if not matches:
            raise ValueError("no supported current reservation representation found")
        if len(matches) > 1:
            raise ValueError("competing current reservation representations; refusing to guess")
        table, id_col = matches[0]
        counts = dict(con.execute(
            "SELECT state, COUNT(*) FROM " + table + " GROUP BY state ORDER BY state"))
        rows = con.execute(
            "SELECT " + id_col + ", asset_id, starts_at, ends_at FROM " + table +
            " WHERE state = 'active' ORDER BY asset_id, " + id_col).fetchall()
    finally:
        con.close()
    after = _digest(p)
    if before != after:
        raise RuntimeError("storage changed during diagnosis; no stable snapshot")
    pairs = []
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            # strict inequalities: adjacency (end == start) is not an overlap
            if a[1] == b[1] and a[2] < b[3] and b[2] < a[3]:
                pairs.append([a[0], b[0]])
    pairs.sort()
    return {
        "diagnosis": "ACTIVE_OVERLAP" if pairs else "NO_ACTIVE_OVERLAP_OBSERVED",
        "counts": counts,
        "active_overlap_pairs": pairs,
        "schema_version": version,
        "representation": table,
        "path": str(p),
        "digest": after,
        "digest_before": before,
        "digest_after": after,
        "unchanged": True,
    }


def _number(value, name):
    if isinstance(value, bool) or value is None:
        raise ValueError(name + " must be a number")
    try:
        d = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError(name + " is not numeric: " + repr(value))
    if not d.is_finite() or d < 0:
        raise ValueError(name + " must be finite and nonnegative: " + repr(value))
    return d


def cost_summary(attempts, accepted):
    if isinstance(accepted, bool) or not isinstance(accepted, int) or accepted < 0:
        raise ValueError("accepted must be a nonnegative integer")
    cost = Decimal(0)
    minutes = Decimal(0)
    n = 0
    for a in attempts:
        try:
            c, m = a["cost_eur"], a["minutes"]
        except (KeyError, TypeError):
            raise ValueError("every attempt needs cost_eur and minutes")
        cost += _number(c, "cost_eur")
        minutes += _number(m, "minutes")
        n += 1
    result = {"attempts": n, "accepted": accepted,
              "total_cost_eur": str(cost), "total_minutes": str(minutes)}
    if accepted == 0:
        result.update(cost_per_accepted_eur=None, minutes_per_accepted=None,
                      status="NO_ACCEPTED_OUTCOME")
    else:
        result.update(cost_per_accepted_eur=str(cost / accepted),
                      minutes_per_accepted=str(minutes / accepted), status="OK")
    return result
