"""G4 diagnosis and accepted-outcome accounting (OPS-G4/v3 + G4-OD-01)."""
from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib
import json
import sqlite3

_REF = ("id", "asset_id", "member_id", "starts_at", "ends_at", "request_key",
        "request_hash", "state", "version")
_REC = ("reservation_id", "trusted_member_id", "asset_id", "starts_at", "ends_at",
        "idempotency_key", "payload_fingerprint", "state", "version")
_NAT = ("id", "trusted_member_id", "asset_id", "starts_at", "ends_at",
        "idempotency_key", "fingerprint", "state", "version")


def _representations():
    """(table, signature, id/asset/start/end/state columns) for each current layout."""
    reps = [("reservations", _REF, _REF[0]),
            ("reservations_v2", _REC, _REC[0]),
            ("reservations_v2", _NAT, _NAT[0])]
    reps = [(t, s, {"id": i, "asset_id": "asset_id", "starts_at": "starts_at",
                    "ends_at": "ends_at", "state": "state"}) for t, s, i in reps]
    path = Path(__file__).resolve().parent / "docs" / "G4-SCHEMA-MAP.json"
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        roles = data["roles"]
        reps.append((data["table"], tuple(data["signature"]),
                     {k: roles[k] for k in ("id", "asset_id", "starts_at", "ends_at", "state")}))
    return reps


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _q(name):
    return '"' + name.replace('"', '""') + '"'


def diagnose(path):
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"storage not found: {p}")
    resolved = p.resolve()
    before = _digest(resolved)
    # mode=ro: never creates or initializes; no writes are issued.
    con = sqlite3.connect(f"{resolved.as_uri()}?mode=ro", uri=True)
    try:
        con.execute("BEGIN")
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version != 3:
            raise ValueError(f"unsupported schema version {version}; schema 3 required")
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        current = []
        for table, signature, cols in _representations():
            if table in tables:
                found = tuple(r[1] for r in con.execute(f"PRAGMA table_info({_q(table)})"))
                if found == signature:
                    current.append((table, cols))
        if not current:
            raise ValueError("no supported current reservation representation")
        if len(current) > 1:
            raise ValueError("competing current representations: "
                             + ", ".join(t for t, _ in current))
        table, c = current[0]
        rows = con.execute(
            f"SELECT {_q(c['id'])}, {_q(c['asset_id'])}, {_q(c['starts_at'])}, "
            f"{_q(c['ends_at'])}, {_q(c['state'])} FROM {_q(table)} ORDER BY {_q(c['id'])}"
        ).fetchall()
        con.execute("ROLLBACK")
    finally:
        con.close()
    after = _digest(resolved)
    if before != after:
        raise RuntimeError("storage changed during diagnosis; no stable snapshot")
    counts = {}
    for _, _, _, _, state in rows:
        counts[state] = counts.get(state, 0) + 1
    active = [r for r in rows if r[4] == "active"]
    pairs = [[a[0], b[0]] for i, a in enumerate(active) for b in active[i + 1:]
             if a[1] == b[1] and a[2] < b[3] and b[2] < a[3]]
    return {"diagnosis": "ACTIVE_OVERLAP" if pairs else "NO_ACTIVE_OVERLAP_OBSERVED",
            "counts": dict(sorted(counts.items())), "active_overlap_pairs": pairs,
            "schema_version": version, "path": str(resolved), "table": table,
            "sha256_before": before, "sha256_after": after, "unchanged": True}


def _dec(value, field):
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    try:
        d = Decimal(str(value).strip()) if isinstance(value, (str, int, Decimal)) \
            else Decimal(repr(value)) if isinstance(value, float) else None
    except InvalidOperation:
        d = None
    if d is None:
        raise ValueError(f"{field} is not a valid number: {value!r}")
    if not d.is_finite() or d < 0:
        raise ValueError(f"{field} must be finite and nonnegative: {value!r}")
    return d


def _fmt(d):
    return format(d, "f")


def cost_summary(attempts, accepted):
    if isinstance(accepted, bool) or not isinstance(accepted, int) or accepted < 0:
        raise ValueError("accepted must be a nonnegative integer")
    attempts = list(attempts)
    cost = sum((_dec(a.get("cost_eur") if isinstance(a, dict) else None, "cost_eur")
                for a in attempts), Decimal(0))
    mins = sum((_dec(a.get("minutes"), "minutes") for a in attempts), Decimal(0))
    r = {"attempts": len(attempts), "accepted": accepted,
         "total_cost_eur": _fmt(cost), "total_minutes": _fmt(mins)}
    if accepted == 0:
        r.update(cost_per_accepted_eur=None, minutes_per_accepted=None,
                 status="NO_ACCEPTED_OUTCOME")
    else:
        r.update(cost_per_accepted_eur=_fmt(cost / accepted),
                 minutes_per_accepted=_fmt(mins / accepted), status="OK")
    return r
