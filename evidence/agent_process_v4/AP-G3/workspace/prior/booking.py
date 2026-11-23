"""Durable G2 reservations with explicit, lossless G1 migrations."""
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import json
import re
import sqlite3


@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False


_PUBLIC = (
    "reservation_id", "trusted_member_id", "asset_id", "starts_at",
    "ends_at", "idempotency_key",
)
_OLD_COLUMNAR = (
    "id", "member_id", "asset_id", "starts_at", "ends_at", "request_key",
)
_CURRENT = _PUBLIC + ("payload_fingerprint",)
_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
_INDEXES = {
    "reservations_v2_identity": (1, ("trusted_member_id", "idempotency_key")),
    "reservations_v2_interval": (0, ("asset_id", "starts_at", "ends_at")),
}


def _invalid_request(member, asset, start, end, key):
    if any(not isinstance(value, str) or not 1 <= len(value) <= 128
           for value in (member, asset, key)):
        return "invalid-identifier"
    if any(not isinstance(value, str) or not _TIMESTAMP.fullmatch(value)
           for value in (start, end)):
        return "invalid-timestamp"
    try:
        first = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
        last = datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return "invalid-timestamp"
    if not timedelta(0) < last - first <= timedelta(hours=24):
        return "invalid-interval"
    return None


def _fingerprint(asset, start, end):
    payload = json.dumps([asset, start, end], ensure_ascii=True,
                         separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _mapping_required(reason):
    return ValueError(f"{reason}; owner mapping required")


def _signature(columns):
    return tuple(
        (name, "INTEGER" if position == 0 else "TEXT",
         0 if position == 0 else 1, None, 1 if position == 0 else 0, 0)
        for position, name in enumerate(columns)
    )


def _table_signature(connection, table):
    # Callers supply only the literal, authorized table names below.
    return tuple(tuple(row[1:]) for row in
                 connection.execute(f"PRAGMA table_xinfo({table})"))


def _legacy_source(connection, tables):
    if not tables:
        return None
    if len(tables) != 1:
        raise _mapping_required("competing legacy tables")
    table = next(iter(tables))
    if table == "reservations":
        signature = _table_signature(connection, table)
        if signature == _signature(_OLD_COLUMNAR):
            columns = _OLD_COLUMNAR
        elif signature == _signature(_PUBLIC):
            columns = _PUBLIC
        else:
            raise _mapping_required("unknown reservations column signature")
    elif table == "bookings_v2":
        columns = ("booking_no", "payload")
        if _table_signature(connection, table) != _signature(columns):
            raise _mapping_required("unknown bookings_v2 column signature")
    else:
        raise _mapping_required("unknown legacy table")
    if (connection.execute(f"PRAGMA index_list({table})").fetchall()
            or connection.execute(f"PRAGMA foreign_key_list({table})").fetchall()):
        raise _mapping_required("unrecognized legacy constraints")
    return table, columns


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise _mapping_required("duplicate legacy JSON property")
        result[key] = value
    return result


def _legacy_rows(connection, source):
    if source is None:
        return []
    table, columns = source
    rows = connection.execute(
        f"SELECT {', '.join(columns)} FROM {table}"
    ).fetchall()
    if table == "bookings_v2":
        decoded = []
        for identifier, raw in rows:
            try:
                if not isinstance(raw, str):
                    raise ValueError("JSON payload is not text")
                payload = json.loads(raw, object_pairs_hook=_json_object)
            except (TypeError, ValueError) as error:
                raise _mapping_required("invalid legacy JSON") from error
            if not isinstance(payload, dict) or set(payload) != set(_PUBLIC[1:]):
                raise _mapping_required("unknown legacy JSON fields")
            decoded.append((identifier, *(payload[name] for name in _PUBLIC[1:])))
        rows = decoded

    # Validate every value before classifying duplicate identities or overlaps.
    for row in rows:
        problem = _invalid_request(*row[1:])
        if type(row[0]) is not int or problem:
            raise _mapping_required(f"invalid legacy record ({problem or 'identifier'})")
    identities = set()
    for row in rows:
        identity = (row[1], row[5])
        if identity in identities:
            raise sqlite3.IntegrityError(
                "duplicate legacy identity; owner mapping required"
            )
        identities.add(identity)
    previous = None
    for row in sorted(rows, key=lambda value: (value[2], value[3])):
        if previous and row[2] == previous[2] and row[3] < previous[4]:
            raise _mapping_required("overlapping legacy intervals")
        previous = row
    return [tuple(row) + (_fingerprint(*row[2:5]),) for row in rows]


def _check_current(connection, tables, indexes):
    if "reservations_v2" not in tables:
        raise _mapping_required("version 2 current table is missing")
    _legacy_source(connection, tables - {"reservations_v2"})
    if _table_signature(connection, "reservations_v2") != _signature(_CURRENT):
        raise _mapping_required("unknown current column signature")
    if indexes != {(name, "reservations_v2") for name in _INDEXES}:
        raise _mapping_required("unknown current indexes")
    actual = connection.execute("PRAGMA index_list(reservations_v2)").fetchall()
    if len(actual) != len(_INDEXES):
        raise _mapping_required("unknown current constraints")
    for _, name, unique, origin, partial in actual:
        definition = connection.execute(f"PRAGMA index_xinfo({name})").fetchall()
        keys = [row for row in definition if row[5]]
        if (name not in _INDEXES or origin != "c" or partial
                or (unique, tuple(row[2] for row in keys)) != _INDEXES[name]
                or any(row[3] != 0 or row[4] != "BINARY" for row in keys)):
            raise _mapping_required("unknown current index definition")
    if connection.execute("PRAGMA foreign_key_list(reservations_v2)").fetchall():
        raise _mapping_required("unknown current foreign keys")


def init_db(path: str | Path) -> None:
    with closing(sqlite3.connect(path)) as connection, connection:
        # SQLite serializes schema decisions with reservation writers.
        connection.execute("BEGIN IMMEDIATE")
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        objects = connection.execute(
            "SELECT type, name, tbl_name FROM sqlite_master "
            "WHERE name NOT GLOB 'sqlite_*'"
        ).fetchall()
        if any(kind not in ("table", "index") for kind, _, _ in objects):
            raise _mapping_required("unknown schema objects")
        tables = {name for kind, name, _ in objects if kind == "table"}
        indexes = {(name, owner) for kind, name, owner in objects if kind == "index"}
        if version == 2:
            _check_current(connection, tables, indexes)
            return
        if version != 0 or indexes:
            raise _mapping_required("unknown schema version or indexes")
        source = _legacy_source(connection, tables)
        rows = _legacy_rows(connection, source)

        # No legacy DDL or row is changed. All validation precedes any new DDL.
        connection.execute("""
            CREATE TABLE reservations_v2 (
                reservation_id INTEGER PRIMARY KEY,
                trusted_member_id TEXT NOT NULL,
                asset_id TEXT NOT NULL,
                starts_at TEXT NOT NULL,
                ends_at TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                payload_fingerprint TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE UNIQUE INDEX reservations_v2_identity
            ON reservations_v2(trusted_member_id, idempotency_key)
        """)
        connection.execute("""
            CREATE INDEX reservations_v2_interval
            ON reservations_v2(asset_id, starts_at, ends_at)
        """)
        connection.executemany("""
            INSERT INTO reservations_v2 (
                reservation_id, trusted_member_id, asset_id, starts_at,
                ends_at, idempotency_key, payload_fingerprint
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, rows)
        connection.execute("PRAGMA user_version = 2")


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    problem = _invalid_request(
        trusted_member_id, asset_id, starts_at, ends_at, idempotency_key
    )
    if problem:
        return Outcome(422, problem)
    fingerprint = _fingerprint(asset_id, starts_at, ends_at)
    with closing(sqlite3.connect(db_path)) as connection, connection:
        # Acquire the write lock before either decision; no stale check can insert.
        connection.execute("BEGIN IMMEDIATE")
        original = connection.execute("""
            SELECT reservation_id, payload_fingerprint, asset_id, starts_at, ends_at
            FROM reservations_v2
            WHERE trusted_member_id = ? AND idempotency_key = ?
        """, (trusted_member_id, idempotency_key)).fetchone()
        if original is not None:
            if (original[1] == fingerprint
                    and original[2:] == (asset_id, starts_at, ends_at)):
                return Outcome(200, "confirmed", original[0], True)
            return Outcome(409, "idempotency-key-reused")
        overlap = connection.execute("""
            SELECT 1 FROM reservations_v2
            WHERE asset_id = ? AND starts_at < ? AND ends_at > ?
            LIMIT 1
        """, (asset_id, ends_at, starts_at)).fetchone()
        if overlap is not None:
            return Outcome(409, "interval-conflict")
        cursor = connection.execute("""
            INSERT INTO reservations_v2 (
                trusted_member_id, asset_id, starts_at, ends_at,
                idempotency_key, payload_fingerprint
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (trusted_member_id, asset_id, starts_at, ends_at,
              idempotency_key, fingerprint))
        reservation_id = cursor.lastrowid
    return Outcome(201, "confirmed", reservation_id)


def get_reservation(path: str | Path, reservation_id: int):
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute("""
            SELECT reservation_id, trusted_member_id, asset_id, starts_at,
                   ends_at, idempotency_key
            FROM reservations_v2
            WHERE reservation_id = ?
        """, (reservation_id,)).fetchone()
    return None if row is None else dict(row)
