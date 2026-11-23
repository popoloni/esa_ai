"""G4 operations (OPS-G4/v3): read-only diagnosis and accepted-outcome cost accounting."""
import hashlib
import os
import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

_REFERENCE = ("id", "asset_id", "member_id", "starts_at", "ends_at",
              "request_key", "request_hash", "state", "version")
_RECORDED = ("reservation_id", "trusted_member_id", "asset_id", "starts_at", "ends_at",
             "idempotency_key", "payload_fingerprint", "state", "version")
_NATIVE = ("id", "trusted_member_id", "asset_id", "starts_at", "ends_at",
           "idempotency_key", "fingerprint", "state", "version")
# (table, exact column signature, id column): the only layouts OPS-G4/v3 names.
_LAYOUTS = (("reservations", _REFERENCE, "id"),
            ("reservations_v2", _RECORDED, "reservation_id"),
            ("reservations_v2", _NATIVE, "id"))


def _fingerprint(path):
    st = os.stat(path)
    return hashlib.sha256(path.read_bytes()).hexdigest(), st.st_size, st.st_mtime_ns


def diagnose(path):
    """Observe an existing schema-3 database without writing; refuse anything else."""
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError("storage not found: " + str(path))
    before = _fingerprint(path)
    con = sqlite3.connect("file:" + str(path) + "?mode=ro", uri=True)
    try:
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version != 3:
            raise ValueError("unsupported schema version %s; OPS-G4/v3 covers schema 3 only" % version)
        found = []
        for table, signature, id_col in _LAYOUTS:
            cols = tuple(r[1] for r in con.execute("PRAGMA table_info(" + table + ")"))
            if cols == signature:
                found.append((table, id_col))
        if not found:
            raise ValueError("no recognized OPS-G4/v3 reservation layout; owner mapping required")
        if len(found) > 1:
            raise ValueError("competing current reservation layouts; owner mapping required")
        table, id_col = found[0]
        rows = con.execute("SELECT " + id_col + ", asset_id, starts_at, ends_at, state FROM "
                           + table + " ORDER BY " + id_col).fetchall()
    finally:
        con.close()
    after = _fingerprint(path)
    if after != before:
        raise RuntimeError("storage changed during diagnosis; no stable snapshot")
    counts = {}
    for r in rows:
        counts[r[4]] = counts.get(r[4], 0) + 1
    active = [r for r in rows if r[4] == "active"]
    pairs = [[a[0], b[0]] for i, a in enumerate(active) for b in active[i + 1:]
             if a[1] == b[1] and a[2] < b[3] and b[2] < a[3]]
    return {"diagnosis": "ACTIVE_OVERLAP" if pairs else "NO_ACTIVE_OVERLAP_OBSERVED",
            "counts": counts, "active_overlap_pairs": pairs, "schema_version": version,
            "path": str(path), "table": table, "sha256": before[0],
            "bytes_unchanged": True}


def _dec(value, field):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError(field + " must be numeric")
    try:
        d = Decimal(value.strip() if isinstance(value, str) else str(value))
    except InvalidOperation:
        raise ValueError("%s is not a number: %r" % (field, value))
    if not d.is_finite() or d < 0:
        raise ValueError("%s must be finite and nonnegative: %r" % (field, value))
    return d


def cost_summary(attempts, accepted):
    """Total all attempts; divide by accepted outcomes supplied by a separate decision."""
    if isinstance(accepted, bool) or not isinstance(accepted, int) or accepted < 0:
        raise ValueError("accepted must be a nonnegative integer")
    cost = minutes = Decimal(0)
    n = 0
    for a in attempts:
        try:
            c, m = a["cost_eur"], a["minutes"]
        except (KeyError, TypeError):
            raise ValueError("each attempt needs cost_eur and minutes")
        cost += _dec(c, "cost_eur")
        minutes += _dec(m, "minutes")
        n += 1
    out = {"attempts": n, "accepted": accepted,
           "total_cost_eur": format(cost, "f"), "total_minutes": format(minutes, "f")}
    if accepted == 0:
        out.update(cost_per_accepted_eur=None, minutes_per_accepted=None,
                   status="NO_ACCEPTED_OUTCOME")
    else:
        out.update(cost_per_accepted_eur=format(cost / accepted, "f"),
                   minutes_per_accepted=format(minutes / accepted, "f"), status="OK")
    return out
