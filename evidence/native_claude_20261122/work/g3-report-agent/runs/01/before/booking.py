"""G3 public interface: validated, idempotent reservations with cancellation.

Contracts RES-001/v1 + G2-OD-01 + G2-OD-02 + RES-002/v1 (docs/). API: init_db,
reserve, get_reservation, reservation_status, cancel. Schema version 3 is
private: table ``reservations_v3`` plus ``PRAGMA user_version = 3``. Earlier
tables (including ``reservations_v2``) are never modified or dropped.
"""
import hashlib
import json
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA_VERSION = 3
_FIELDS = ("trusted_member_id", "asset_id", "starts_at", "ends_at",
           "idempotency_key")
_TS = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")

# Authorized legacy representations (exact column signatures).
_G1_COLUMNS = ["id", "member_id", "asset_id", "starts_at", "ends_at",
               "request_key"]
_RECORDED_COLUMNS = ["reservation_id", "trusted_member_id", "asset_id",
                     "starts_at", "ends_at", "idempotency_key"]
_JSON_COLUMNS = ["booking_no", "payload"]


@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False


def _parse(value):
    if not isinstance(value, str) or not _TS.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except ValueError:
        return None


def _validate(member, asset, start, end, key):
    """Return None if valid, else (status, code)."""
    for v in (member, asset, key):
        if not isinstance(v, str) or not 1 <= len(v) <= 128:
            return 422, "invalid-identifier"
    s, e = _parse(start), _parse(end)
    if s is None or e is None:
        return 422, "invalid-timestamp"
    if not timedelta(0) < e - s <= timedelta(hours=24):
        return 422, "invalid-interval"
    return None


def _fingerprint(asset, start, end):
    return hashlib.sha256(json.dumps([asset, start, end]).encode()).hexdigest()


def _columns(conn, table):
    quoted = '"' + table.replace('"', '""') + '"'
    return [r[1] for r in conn.execute("PRAGMA table_info(" + quoted + ")")]


def _legacy_rows(conn, table, columns):
    """Return (id, member, asset, start, end, key) tuples from a legacy table."""
    quoted = '"' + table.replace('"', '""') + '"'
    rows = conn.execute("SELECT * FROM " + quoted + " ORDER BY 1").fetchall()
    out = []
    for row in rows:
        if columns == _JSON_COLUMNS:
            try:
                p = json.loads(row[1])
            except (TypeError, ValueError):
                raise ValueError(f"unreadable legacy JSON in {table}; owner mapping required")
            if not isinstance(p, dict) or set(p) != set(_FIELDS):
                raise ValueError(f"unknown legacy payload in {table}; owner mapping required")
            row = (row[0],) + tuple(p[f] for f in _FIELDS)
        if type(row[0]) is not int:
            raise ValueError(f"non-integer legacy identifier in {table}")
        out.append(tuple(row))
    return out


def _migrate(conn, table, columns):
    rows = _legacy_rows(conn, table, columns)
    for rid, member, asset, start, end, key in rows:
        bad = _validate(member, asset, start, end, key)
        if bad:
            raise ValueError(f"invalid legacy row {rid} ({bad[1]}); owner mapping required")
    seen = set()
    for rid, member, asset, start, end, key in rows:
        if (member, key) in seen:
            raise sqlite3.IntegrityError(
                f"duplicate legacy identity {(member, key)!r}; owner mapping required")
        seen.add((member, key))
    accepted = []
    for rid, member, asset, start, end, key in rows:
        for a, s, e in accepted:
            if a == asset and s < end and start < e:
                raise ValueError(f"overlapping legacy row {rid}; owner mapping required")
        accepted.append((asset, start, end))
    _create_v3(conn)
    for rid, member, asset, start, end, key in rows:
        conn.execute(
            "INSERT INTO reservations_v3 (id, trusted_member_id, asset_id, "
            "starts_at, ends_at, idempotency_key, fingerprint) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (rid, member, asset, start, end, key,
             _fingerprint(asset, start, end)))


def _create_v3(conn):
    conn.execute(
        "CREATE TABLE reservations_v3 ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "trusted_member_id TEXT NOT NULL, asset_id TEXT NOT NULL, "
        "starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, "
        "idempotency_key TEXT NOT NULL, fingerprint TEXT NOT NULL, "
        "state TEXT NOT NULL DEFAULT 'active' "
        "CHECK (state IN ('active', 'cancelled')), "
        "version INTEGER NOT NULL DEFAULT 1, "
        "UNIQUE (trusted_member_id, idempotency_key))")
    conn.execute("CREATE INDEX reservations_v3_slot "
                 "ON reservations_v3 (asset_id, starts_at, ends_at, state)")


# G2 layout written by legacy_booking.py (schema 2, table ``reservations``).
_G2_REF_COLUMNS = {"id", "asset_id", "member_id", "starts_at", "ends_at",
                   "request_key", "request_hash"}


def _migrate_g2(conn, tables):
    """Copy schema-2 rows to v3 as active/version 1, keeping IDs and fields."""
    if "reservations_v2" in tables:
        if "reservations" in tables and set(_columns(conn, "reservations")) \
                == _G2_REF_COLUMNS:
            raise ValueError("competing schema-2 tables; owner mapping required")
        sql = ("SELECT id, trusted_member_id, asset_id, starts_at, ends_at, "
               "idempotency_key FROM reservations_v2 ORDER BY id")
    elif "reservations" in tables and set(_columns(conn, "reservations")) \
            == _G2_REF_COLUMNS:
        sql = ("SELECT id, member_id, asset_id, starts_at, ends_at, "
               "request_key FROM reservations ORDER BY id")
    else:
        raise ValueError("schema version 2 without a known reservations table; "
                         "owner mapping required")
    rows = conn.execute(sql).fetchall()
    _create_v3(conn)
    for rid, member, asset, start, end, key in rows:
        conn.execute(
            "INSERT INTO reservations_v3 (id, trusted_member_id, asset_id, "
            "starts_at, ends_at, idempotency_key, fingerprint, state, version)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, 'active', 1)",
            (rid, member, asset, start, end, key,
             _fingerprint(asset, start, end)))


def init_db(path: str | Path) -> None:
    """Create or migrate to schema 3; idempotent. Refusal leaves bytes unchanged."""
    conn = sqlite3.connect(path, isolation_level=None, timeout=30)
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'")]
            if version == SCHEMA_VERSION:
                if "reservations_v3" not in tables:
                    raise ValueError("schema version 3 without reservations_v3")
            elif version == 2:
                _migrate_g2(conn, tables)
            elif version != 0:
                raise ValueError(f"unknown schema version {version}")
            elif not tables:
                _create_v3(conn)
            else:
                found = []
                for t in tables:
                    cols = _columns(conn, t)
                    if (t == "reservations" and cols in (_G1_COLUMNS, _RECORDED_COLUMNS)) \
                            or (t == "bookings_v2" and cols == _JSON_COLUMNS):
                        found.append((t, cols))
                    else:
                        raise ValueError(f"unknown table {t!r}; owner mapping required")
                if len(found) != 1:
                    raise ValueError("competing legacy tables; owner mapping required")
                _migrate(conn, *found[0])
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.close()


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    bad = _validate(trusted_member_id, asset_id, starts_at, ends_at,
                    idempotency_key)
    if bad:
        return Outcome(*bad)
    fp = _fingerprint(asset_id, starts_at, ends_at)
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=30)
    try:
        conn.execute("BEGIN IMMEDIATE")  # check and insert are one write txn
        try:
            row = conn.execute(
                "SELECT id, fingerprint FROM reservations_v3 WHERE "
                "trusted_member_id = ? AND idempotency_key = ?",
                (trusted_member_id, idempotency_key)).fetchone()
            if row:
                outcome = (Outcome(200, "confirmed", row[0], True)
                           if row[1] == fp else
                           Outcome(409, "idempotency-key-reused"))
            elif conn.execute(
                    "SELECT 1 FROM reservations_v3 WHERE asset_id = ? "
                    "AND state = 'active' AND starts_at < ? AND ? < ends_at",
                    (asset_id, ends_at, starts_at)).fetchone():
                outcome = Outcome(409, "interval-conflict")
            else:
                cur = conn.execute(
                    "INSERT INTO reservations_v3 (trusted_member_id, asset_id, "
                    "starts_at, ends_at, idempotency_key, fingerprint) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (trusted_member_id, asset_id, starts_at, ends_at,
                     idempotency_key, fp))
                outcome = Outcome(201, "confirmed", cur.lastrowid, False)
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        return outcome
    finally:
        conn.close()


def get_reservation(path: str | Path, reservation_id: int):
    # Read-only URI: a missing file raises sqlite3.OperationalError, not created.
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        row = conn.execute(
            "SELECT id, trusted_member_id, asset_id, starts_at, ends_at, "
            "idempotency_key FROM reservations_v3 WHERE id = ?",
            (reservation_id,)).fetchone()
    if row is None:
        return None
    return {"reservation_id": row[0], **dict(zip(_FIELDS, row[1:]))}


def reservation_status(path, reservation_id):
    """Return {"state", "version"} for the reservation, or None if missing."""
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        row = conn.execute(
            "SELECT state, version FROM reservations_v3 WHERE id = ?",
            (reservation_id,)).fetchone()
    return None if row is None else {"state": row[0], "version": row[1]}


def cancel(path, reservation_id, *, trusted_member_id, expected_version):
    """Cancel atomically; returns {"status", "code"[, "version"]}.

    Checks in order: 404 not-found, 403 not-owner, 409 stale-version; those
    change nothing. Success is 200 cancelled (version + 1) or 200
    already-cancelled (current cancelled version, no change).
    """
    conn = sqlite3.connect(path, isolation_level=None, timeout=30)
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            row = conn.execute(
                "SELECT trusted_member_id, state, version FROM "
                "reservations_v3 WHERE id = ?", (reservation_id,)).fetchone()
            if row is None:
                result = {"status": 404, "code": "not-found"}
            elif row[0] != trusted_member_id:
                result = {"status": 403, "code": "not-owner"}
            elif row[2] != expected_version:
                result = {"status": 409, "code": "stale-version"}
            elif row[1] == "cancelled":
                result = {"status": 200, "code": "already-cancelled",
                          "version": row[2]}
            else:
                conn.execute(
                    "UPDATE reservations_v3 SET state = 'cancelled', "
                    "version = version + 1 WHERE id = ?", (reservation_id,))
                result = {"status": 200, "code": "cancelled",
                          "version": row[2] + 1}
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
        return result
    finally:
        conn.close()
