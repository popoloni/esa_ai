"""G4 diagnosis and accepted-outcome accounting (OPS-G4/v3). Read-only; no repair."""
import hashlib
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

_REFERENCE = ("id", "asset_id", "member_id", "starts_at", "ends_at", "request_key", "request_hash", "state", "version")
_RECORDED = ("reservation_id", "trusted_member_id", "asset_id", "starts_at", "ends_at", "idempotency_key", "payload_fingerprint", "state", "version")
_NATIVE = ("id", "trusted_member_id", "asset_id", "starts_at", "ends_at", "idempotency_key", "fingerprint", "state", "version")
# (table, full column signature, id column)
_SUPPORTED = (("reservations", _REFERENCE, "id"),
              ("reservations_v2", _RECORDED, "reservation_id"),
              ("reservations_v2", _NATIVE, "id"))


def _digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ts(text):
    return datetime.fromisoformat(str(text).replace("Z", "+00:00"))


def diagnose(path):
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError("storage does not exist: %s" % p)
    resolved = p.resolve()
    before = _digest(resolved)
    uri = "file:" + resolved.as_posix().replace("%", "%25").replace("?", "%3f").replace("#", "%23") + "?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version != 3:
            raise ValueError("unsupported schema version %r; only G3 schema 3 is recognized" % version)
        matches = []
        for table, signature, id_col in _SUPPORTED:
            found = tuple(r[1] for r in con.execute("PRAGMA table_info(%s)" % table))
            if found == signature:
                matches.append((table, id_col))
        if not matches:
            raise ValueError("no supported current reservation representation")
        if len(matches) > 1:
            raise ValueError("competing current reservation representations; refusing to guess")
        table, id_col = matches[0]
        rows = con.execute("SELECT %s, asset_id, starts_at, ends_at, state FROM %s ORDER BY %s" % (id_col, table, id_col)).fetchall()
    finally:
        con.close()
    after = _digest(resolved)
    if before != after:
        raise RuntimeError("storage changed during diagnosis; no stable snapshot")
    counts = {}
    for r in rows:
        counts[r[4]] = counts.get(r[4], 0) + 1
    active = [(r[0], r[1], _ts(r[2]), _ts(r[3])) for r in rows if r[4] == "active"]
    pairs = []
    for i, a in enumerate(active):
        for b in active[i + 1:]:
            if a[1] == b[1] and a[2] < b[3] and b[2] < a[3]:  # adjacency excluded
                pairs.append([a[0], b[0]])
    return {"diagnosis": "ACTIVE_OVERLAP" if pairs else "NO_ACTIVE_OVERLAP_OBSERVED",
            "counts": counts, "active_overlap_pairs": pairs,
            "schema_version": version, "path": str(resolved),
            "digest": after, "table": table,
            "unchanged": True, "repair": "NOT_PERFORMED"}


def _dec(value, name):
    if isinstance(value, bool) or value is None:
        raise ValueError("%s must be numeric" % name)
    try:
        d = Decimal(repr(value) if isinstance(value, float) else str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("%s is not a number: %r" % (name, value))
    if not d.is_finite() or d < 0:
        raise ValueError("%s must be finite and nonnegative: %r" % (name, value))
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
        cost += _dec(c, "cost_eur")
        minutes += _dec(m, "minutes")
        n += 1
    out = {"attempts": n, "accepted": accepted,
           "total_cost_eur": str(cost), "total_minutes": str(minutes)}
    if accepted == 0:
        out.update(cost_per_accepted_eur=None, minutes_per_accepted=None, status="NO_ACCEPTED_OUTCOME")
    else:
        out.update(cost_per_accepted_eur=str(cost / accepted), minutes_per_accepted=str(minutes / accepted), status="OK")
    return out
