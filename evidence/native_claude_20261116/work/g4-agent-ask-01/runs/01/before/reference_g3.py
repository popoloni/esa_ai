"""Teaching reference: the first durable reservation slice,
not a deployable API.

The caller provides trusted member identity.
Authentication, HTTP, production monitoring, rate
limiting, backups, and deployment are deliberately out of
scope.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
import sqlite3
from pathlib import Path
from contextlib import closing


@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False


def _init_v2(path: str | Path) -> None:
    """Atomic teaching migration from either supplied G1
    schema; retain old tables.
    """
    con = sqlite3.connect(str(path), timeout=10, isolation_level=None)
    try:
        con.execute("BEGIN IMMEDIATE")
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 2):
            raise ValueError("unsupported reservation schema")
        tables = {x[0] for x in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        prior = []
        if version == 0 and {"reservations", "bookings_v2"} <= tables:
            raise ValueError("two legacy representations require an owner mapping")
        if version == 0 and "reservations" in tables:
            columns = {x[1] for x in con.execute("PRAGMA table_info(reservations)")}
            if columns != {"id", "member_id", "asset_id", "starts_at", "ends_at", "request_key"}:
                raise ValueError("unknown legacy schema; owner mapping required")
            prior = list(con.execute("""
            SELECT id , member_id , asset_id , starts_at , ends_at ,
            request_key FROM reservations
            """))
            con.execute("""
            ALTER TABLE reservations RENAME TO
            archived_g1_reservations
            """)
        elif version == 0 and "bookings_v2" in tables:
            for identifier, payload in con.execute("SELECT booking_no,payload FROM bookings_v2"):
                p = json.loads(payload)
                prior.append((identifier, p["trusted_member_id"], p["asset_id"], p["starts_at"], p["ends_at"], p["idempotency_key"]))
        elif version == 0 and tables:
            raise ValueError("unknown legacy schema; owner mapping required")
        con.execute("""
            CREATE TABLE IF NOT EXISTS reservations ( id INTEGER
            PRIMARY KEY AUTOINCREMENT , asset_id TEXT NOT NULL ,
            member_id TEXT NOT NULL , starts_at TEXT NOT NULL ,
            ends_at TEXT NOT NULL , request_key TEXT NOT NULL ,
            request_hash TEXT NOT NULL , UNIQUE ( member_id ,
            request_key ) )
        """)
        for identifier, member, asset, start, end, key in prior:
            if type(identifier) is not int or identifier < 1 or not all(isinstance(x, str) and x.strip() and len(x) <= 128 for x in (member, asset, key)):
                raise ValueError("invalid legacy identity; owner mapping required")
            if not timedelta(0) < _parse_utc_seconds(end) - _parse_utc_seconds(start) <= timedelta(hours=24):
                raise ValueError("invalid legacy interval; owner mapping required")
            request_hash = hashlib.sha256(json.dumps([asset,start,end], separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
            con.execute("INSERT INTO reservations VALUES(?,?,?,?,?,?,?)",
                        (identifier, asset, member, start, end, key, request_hash))
        if prior and con.execute("""
            SELECT 1 FROM reservations a JOIN reservations b ON a .
            id < b . id AND a . asset_id = b . asset_id AND a .
            starts_at < b . ends_at AND b . starts_at < a . ends_at
            LIMIT 1
        """).fetchone():
            raise ValueError("overlapping legacy rows require an owner mapping")
        con.execute("""
            CREATE INDEX IF NOT EXISTS ix_res_asset_time ON
            reservations ( asset_id , starts_at , ends_at )
        """)
        con.execute("PRAGMA user_version=2")
        con.execute("COMMIT")
    except BaseException:
        if con.in_transaction: con.execute("ROLLBACK")
        raise
    finally:
        con.close()


def init_db(path: str | Path) -> None:
    with closing(sqlite3.connect(path)) as check:
        version = check.execute("PRAGMA user_version").fetchone()[0]
    if version != 3:
        _init_v2(path)
    con = sqlite3.connect(path, isolation_level=None)
    try:
        con.execute("BEGIN IMMEDIATE")
        columns = {x[1] for x in con.execute("PRAGMA table_info(reservations)")}
        if "state" not in columns:
            con.execute("""
            ALTER TABLE reservations ADD COLUMN state TEXT NOT NULL
            DEFAULT 'active'
            """)
            con.execute("""
            ALTER TABLE reservations ADD COLUMN version INTEGER NOT
            NULL DEFAULT 1
            """)
        con.execute("PRAGMA user_version=3")
        con.execute("COMMIT")
    except BaseException:
        if con.in_transaction: con.execute("ROLLBACK")
        raise
    finally: con.close()


def _parse_utc_seconds(timestamp: str) -> datetime:
    # Strict canonical form also preserves chronological ordering as TEXT.
    if not isinstance(timestamp, str) or len(timestamp) != 20 or not timestamp.endswith('Z'):
        raise ValueError('timestamp must be YYYY-MM-DDTHH:MM:SSZ')
    dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    if dt.strftime('%Y-%m-%dT%H:%M:%SZ') != timestamp:
        raise ValueError('noncanonical timestamp')
    return dt


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    """Reserve [start,end) for an authenticated caller;
    never trusts payload identity.
    """
    if not all(
        isinstance(x, str) and x.strip() and len(x) <= 128
        for x in (trusted_member_id, asset_id, idempotency_key)
    ):
        return Outcome(422, 'invalid-identifier')
    try:
        start = _parse_utc_seconds(starts_at)
        end = _parse_utc_seconds(ends_at)
    except (ValueError, TypeError):
        return Outcome(422, 'invalid-timestamp')
    if not timedelta(0) < end - start <= timedelta(hours=24):
        return Outcome(422, 'invalid-interval')

    fingerprint = hashlib.sha256(json.dumps(
        [asset_id, starts_at, ends_at],
        separators=(',', ':'), ensure_ascii=True
    ).encode('utf-8')).hexdigest()
    con = sqlite3.connect(
        str(db_path), timeout=10, isolation_level=None
    )
    try:
        con.execute('PRAGMA busy_timeout=10000')
        # One transaction protects both check and insert.
        con.execute('BEGIN IMMEDIATE')
        prior = con.execute("""
            SELECT id, request_hash FROM reservations
            WHERE member_id = ? AND request_key = ?
        """, (trusted_member_id, idempotency_key)).fetchone()
        if prior is not None:
            con.execute('COMMIT')
            if prior[1] == fingerprint:
                return Outcome(
                    200, 'confirmed', prior[0], replayed=True
                )
            return Outcome(409, 'idempotency-key-reused')
        clash = con.execute("""
            SELECT 1 FROM reservations
            WHERE asset_id = ? AND state = 'active'
              AND starts_at < ? AND ends_at > ?
            LIMIT 1
        """, (asset_id, ends_at, starts_at)).fetchone()
        if clash is not None:
            con.execute('COMMIT')
            return Outcome(409, 'interval-conflict')
        cursor = con.execute("""
            INSERT INTO reservations (
                asset_id, member_id, starts_at, ends_at,
                request_key, request_hash
            ) VALUES (?,?,?,?,?,?)
        """, (asset_id, trusted_member_id, starts_at, ends_at,
              idempotency_key, fingerprint))
        reservation_id = cursor.lastrowid
        con.execute('COMMIT')
        return Outcome(201, 'confirmed', reservation_id)
    except Exception:
        if con.in_transaction:
            con.execute('ROLLBACK')
        raise
    finally:
        con.close()


def get_reservation(path: str | Path, reservation_id: int) -> dict | None:
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)) as con:
        row = con.execute("""
            SELECT id , member_id , asset_id , starts_at , ends_at ,
            request_key FROM reservations WHERE id = ?
        """, (reservation_id,)).fetchone()
    if row is None:
        return None
    return dict(zip(("reservation_id", "trusted_member_id", "asset_id",
                     "starts_at", "ends_at", "idempotency_key"), row))


def reservation_status(path, reservation_id):
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)) as con:
        row = con.execute("SELECT state,version FROM reservations WHERE id=?", (reservation_id,)).fetchone()
    return None if row is None else {"state":row[0], "version":row[1]}


def cancel(
    path, reservation_id, *, trusted_member_id, expected_version
):
    con = sqlite3.connect(path, isolation_level=None, timeout=10)
    try:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("""
            SELECT member_id, state, version FROM reservations
            WHERE id=?
        """, (reservation_id,)).fetchone()
        if row is None:
            result = {"status":404, "code":"not-found"}
        elif row[0] != trusted_member_id:
            result = {"status":403, "code":"not-owner"}
        elif row[2] != expected_version:
            result = {"status":409, "code":"stale-version"}
        elif row[1] == "cancelled":
            result = {"status":200, "code":"already-cancelled",
                      "version":row[2]}
        else:
            con.execute("""
                UPDATE reservations SET state='cancelled',
                version=version+1 WHERE id=?
            """, (reservation_id,))
            result = {"status":200, "code":"cancelled",
                      "version":row[2]+1}
        con.execute("COMMIT")
        return result
    except BaseException:
        if con.in_transaction:
            con.execute("ROLLBACK")
        raise
    finally:
        con.close()
