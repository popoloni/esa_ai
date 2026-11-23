"""G2 public interface: validated, idempotent, non-overlapping reservations.

Contract: RES-001/v1 + G2-OD-01 + G2-OD-02. Schema version 2 lives in
``reservations_v2``; legacy G1 tables are migrated from, never modified.
Concurrency claims apply to local SQLite in one tested process environment only.
"""
import hashlib
import json
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

SCHEMA_VERSION = 2
_TABLE = "reservations_v2"
_TIMEOUT = 30.0


@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False


_SCHEMA = f"""CREATE TABLE {_TABLE} (
    id INTEGER PRIMARY KEY,
    trusted_member_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    UNIQUE (trusted_member_id, idempotency_key))"""
_INDEX = f"CREATE INDEX {_TABLE}_asset_time ON {_TABLE} (asset_id, starts_at, ends_at)"

_FIELDS = ("trusted_member_id", "asset_id", "starts_at", "ends_at", "idempotency_key")
# G1 columnar signatures authorized by G2-OD-01 (legacy_g1) and G2-OD-02 (retained AP-G1).
_COLUMNAR_G1 = ["id", "member_id", "asset_id", "starts_at", "ends_at", "request_key"]
_COLUMNAR_RECORDED = ["reservation_id", "trusted_member_id", "asset_id",
                      "starts_at", "ends_at", "idempotency_key"]
_TS = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")


def _ident_ok(value) -> bool:
    return isinstance(value, str) and 0 < len(value) <= 128


def _parse(value):
    if not isinstance(value, str) or not _TS.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


def _validate(member, asset, start, end, key) -> str | None:
    """Return a distinct 422 code, or None when the request is valid."""
    if not all(_ident_ok(v) for v in (member, asset, key)):
        return "invalid-identifier"
    s, e = _parse(start), _parse(end)
    if s is None or e is None:
        return "invalid-timestamp"
    if not (timedelta(0) < e - s <= timedelta(hours=24)):
        return "invalid-interval"
    return None


def _fingerprint(asset, start, end) -> str:
    return hashlib.sha256(json.dumps([asset, start, end]).encode()).hexdigest()


def _connect(path, **kw):
    conn = sqlite3.connect(path, timeout=_TIMEOUT, isolation_level=None, **kw)
    return conn


def _tables(conn):
    return [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]


def _columns(conn, table):
    quoted = '"' + table.replace('"', '""') + '"'
    return [r[1] for r in conn.execute(f"PRAGMA table_info({quoted})")]


def _legacy_rows(conn, tables):
    """Return public-field tuples (id, member, asset, start, end, key) from the single
    authorized legacy source, or raise ValueError when the schema is not authorized."""
    if len(tables) != 1:
        raise ValueError(f"owner mapping required: unsupported or competing tables {sorted(tables)}")
    name = tables[0]
    if name == "reservations":
        cols = _columns(conn, name)
        if cols not in (_COLUMNAR_G1, _COLUMNAR_RECORDED):
            raise ValueError(f"owner mapping required: unknown columns {cols}")
        q = ", ".join('"' + c + '"' for c in cols)
        return [tuple(r) for r in conn.execute(f'SELECT {q} FROM "reservations" ORDER BY 1')]
    if name == "bookings_v2":
        if _columns(conn, name) != ["booking_no", "payload"]:
            raise ValueError("owner mapping required: unknown bookings_v2 columns")
        rows = []
        for no, payload in conn.execute("SELECT booking_no, payload FROM bookings_v2 ORDER BY 1"):
            try:
                data = json.loads(payload)
            except (TypeError, ValueError):
                raise ValueError(f"owner mapping required: unreadable payload for {no}")
            if not isinstance(data, dict) or set(data) != set(_FIELDS):
                raise ValueError(f"owner mapping required: unexpected payload fields for {no}")
            rows.append((no, *(data[f] for f in _FIELDS)))
        return rows
    raise ValueError(f"owner mapping required: unknown schema table {name!r}")


def _check_legacy(rows):
    for rid, member, asset, start, end, key in rows:
        if not isinstance(rid, int) or _validate(member, asset, start, end, key):
            raise ValueError(f"owner mapping required: invalid legacy record {rid!r}")
    seen = set()
    for rid, member, _a, _s, _e, key in rows:
        if (member, key) in seen:
            raise sqlite3.IntegrityError(
                f"owner mapping required: duplicate legacy identity {(member, key)!r}")
        seen.add((member, key))
    last_end = {}
    for rid, _m, asset, start, end, _k in sorted(rows, key=lambda r: (r[2], r[3], r[4])):
        if asset in last_end and start < last_end[asset]:
            raise ValueError(f"owner mapping required: overlapping legacy intervals at {rid}")
        last_end[asset] = max(end, last_end.get(asset, end))


def init_db(path: str | Path) -> None:
    """Create or migrate to schema v2 in one transaction; refuse without any change."""
    with closing(_connect(path)) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            tables = _tables(conn)
            if version == SCHEMA_VERSION:
                if _TABLE not in tables:
                    raise ValueError("schema version 2 marker without reservation table")
            elif version != 0:
                raise ValueError(f"unsupported schema version {version}")
            else:
                legacy = [t for t in tables if t != _TABLE]
                rows = _legacy_rows(conn, legacy) if tables else []
                if _TABLE in tables:
                    raise ValueError("unversioned database already contains the v2 table")
                _check_legacy(rows)
                conn.execute(_SCHEMA)
                conn.execute(_INDEX)
                conn.executemany(
                    f"INSERT INTO {_TABLE} (id, trusted_member_id, asset_id, starts_at,"
                    " ends_at, idempotency_key, fingerprint) VALUES (?,?,?,?,?,?,?)",
                    [(r[0], r[1], r[2], r[3], r[4], r[5], _fingerprint(r[2], r[3], r[4]))
                     for r in rows])
                conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    code = _validate(trusted_member_id, asset_id, starts_at, ends_at, idempotency_key)
    if code:
        return Outcome(422, code)
    fp = _fingerprint(asset_id, starts_at, ends_at)
    with closing(_connect(db_path)) as conn:
        conn.execute("BEGIN IMMEDIATE")  # check and insert are one write transaction
        try:
            row = conn.execute(
                f"SELECT id, fingerprint FROM {_TABLE} WHERE trusted_member_id = ?"
                " AND idempotency_key = ?", (trusted_member_id, idempotency_key)).fetchone()
            if row is not None:
                outcome = (Outcome(200, "confirmed", row[0], True) if row[1] == fp
                           else Outcome(409, "idempotency-key-reused"))
            elif conn.execute(
                    f"SELECT 1 FROM {_TABLE} WHERE asset_id = ? AND starts_at < ?"
                    " AND ends_at > ? LIMIT 1", (asset_id, ends_at, starts_at)).fetchone():
                outcome = Outcome(409, "interval-conflict")
            else:
                cur = conn.execute(
                    f"INSERT INTO {_TABLE} (trusted_member_id, asset_id, starts_at, ends_at,"
                    " idempotency_key, fingerprint) VALUES (?,?,?,?,?,?)",
                    (trusted_member_id, asset_id, starts_at, ends_at, idempotency_key, fp))
                outcome = Outcome(201, "confirmed", cur.lastrowid)
            conn.execute("COMMIT")
            return outcome
        except BaseException:
            conn.execute("ROLLBACK")
            raise


def get_reservation(path: str | Path, reservation_id: int):
    # Missing file -> sqlite3.OperationalError; mode=ro never creates or mutates.
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        row = conn.execute(
            f"SELECT id, trusted_member_id, asset_id, starts_at, ends_at,"
            f" idempotency_key FROM {_TABLE} WHERE id = ?", (reservation_id,)).fetchone()
    if row is None:
        return None
    keys = ("reservation_id", "trusted_member_id", "asset_id", "starts_at",
            "ends_at", "idempotency_key")
    return dict(zip(keys, row))
