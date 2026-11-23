"""Durable reservations with lossless migrations and owner-only cancellation."""
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
_STATE_SIGNATURE = (
    ("state", "TEXT", 1, "'active'", 0, 0),
    ("version", "INTEGER", 1, "1", 0, 0),
)
_SUPPLIED_G2 = (
    "id", "asset_id", "member_id", "starts_at", "ends_at",
    "request_key", "request_hash",
)
_SUPPLIED_INDEXES = {
    "sqlite_autoindex_reservations_1": (1, ("member_id", "request_key"), "u"),
    "ix_res_asset_time": (0, ("asset_id", "starts_at", "ends_at"), "c"),
}
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

    return _validated_legacy_rows(rows)


def _validated_legacy_rows(rows):
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


def _check_indexes(connection, table, expected):
    actual = connection.execute(f"PRAGMA index_list({table})").fetchall()
    if len(actual) != len(expected):
        raise _mapping_required("unknown current constraints")
    for _, name, unique, origin, partial in actual:
        # Only inspect authorized literal index names.
        if name not in expected:
            raise _mapping_required("unknown current index")
        definition = connection.execute(f"PRAGMA index_xinfo({name})").fetchall()
        keys = [row for row in definition if row[5]]
        if (partial
                or (unique, tuple(row[2] for row in keys), origin) != expected[name]
                or any(row[3] != 0 or row[4] != "BINARY" for row in keys)):
            raise _mapping_required("unknown current index definition")
    if connection.execute(f"PRAGMA foreign_key_list({table})").fetchall():
        raise _mapping_required("unknown current foreign keys")


def _check_supplied_g2(connection, tables, indexes):
    """Recognize the exact alternate G2 representation supplied with this task."""
    if ("reservations" not in tables
            or _table_signature(connection, "reservations") != _signature(_SUPPLIED_G2)):
        raise _mapping_required("unknown supplied G2 column signature")
    if indexes != {("ix_res_asset_time", "reservations")}:
        raise _mapping_required("unknown supplied G2 indexes")
    _check_indexes(connection, "reservations", _SUPPLIED_INDEXES)
    archives = tables - {"reservations"}
    if archives == {"archived_g1_reservations"}:
        if (_table_signature(connection, "archived_g1_reservations")
                != _signature(_OLD_COLUMNAR)
                or connection.execute(
                    "PRAGMA index_list(archived_g1_reservations)").fetchall()
                or connection.execute(
                    "PRAGMA foreign_key_list(archived_g1_reservations)").fetchall()):
            raise _mapping_required("unknown supplied G1 archive")
    elif archives:
        if archives != {"bookings_v2"}:
            raise _mapping_required("unknown supplied G2 archive")
        _legacy_source(connection, archives)


def _supplied_g2_rows(connection):
    rows = connection.execute("""
        SELECT id, member_id, asset_id, starts_at, ends_at, request_key, request_hash
        FROM reservations
    """).fetchall()
    validated = _validated_legacy_rows([row[:6] for row in rows])
    if any(row[6] != checked[6] for row, checked in zip(rows, validated)):
        raise _mapping_required("inconsistent supplied G2 fingerprint")
    return rows


def _check_current(connection, tables, indexes, version):
    if "reservations_v2" not in tables:
        raise _mapping_required("current table is missing")
    expected = _signature(_CURRENT) + (_STATE_SIGNATURE if version == 3 else ())
    if _table_signature(connection, "reservations_v2") != expected:
        raise _mapping_required("unknown current column signature")
    current_indexes = {(name, "reservations_v2") for name in _INDEXES}
    if not current_indexes <= indexes:
        raise _mapping_required("missing current indexes")
    other_tables = tables - {"reservations_v2"}
    other_indexes = indexes - current_indexes
    if (version == 3 and "reservations" in other_tables
            and _table_signature(connection, "reservations") == _signature(_SUPPLIED_G2)):
        # The alternate G2 table is retained as immutable migration history.
        _check_supplied_g2(connection, other_tables, other_indexes)
    else:
        if other_indexes:
            raise _mapping_required("unknown current indexes")
        _legacy_source(connection, other_tables)
    _check_indexes(connection, "reservations_v2", {
        name: (unique, columns, "c")
        for name, (unique, columns) in _INDEXES.items()
    })


def _create_current(connection, rows):
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


def init_db(path: str | Path) -> None:
    with closing(sqlite3.connect(path)) as connection, connection:
        # Serialize all schema decisions with reservation and cancellation writers.
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
        if version == 3:
            _check_current(connection, tables, indexes, version)
            return
        if version == 2 and "reservations_v2" in tables:
            # Upgrade the actual retained candidate in place, preserving every row.
            _check_current(connection, tables, indexes, version)
        else:
            if version == 2:
                _check_supplied_g2(connection, tables, indexes)
                rows = _supplied_g2_rows(connection)
            elif version == 0 and not indexes:
                source = _legacy_source(connection, tables)
                rows = _legacy_rows(connection, source)
            else:
                raise _mapping_required("unknown schema version or indexes")
            # All source validation precedes DDL; legacy tables and rows stay intact.
            _create_current(connection, rows)
        connection.execute("""
            ALTER TABLE reservations_v2 ADD COLUMN state TEXT NOT NULL
            DEFAULT 'active' CHECK (state IN ('active', 'cancelled'))
        """)
        connection.execute("""
            ALTER TABLE reservations_v2 ADD COLUMN version INTEGER NOT NULL
            DEFAULT 1 CHECK (version >= 1)
        """)
        connection.execute("PRAGMA user_version = 3")


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
            WHERE asset_id = ? AND state = 'active'
              AND starts_at < ? AND ends_at > ?
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


def reservation_status(path: str | Path, reservation_id: int):
    """Read current state without changing the six-field historical read API."""
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        row = connection.execute("""
            SELECT state, version FROM reservations_v2 WHERE reservation_id = ?
        """, (reservation_id,)).fetchone()
    return None if row is None else {"state": row[0], "version": row[1]}


def cancel(path: str | Path, reservation_id: int, *,
           trusted_member_id: str, expected_version: int):
    """Cancel for the trusted owner using an atomic optimistic version check."""
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute("""
            SELECT trusted_member_id, state, version
            FROM reservations_v2 WHERE reservation_id = ?
        """, (reservation_id,)).fetchone()
        if row is None:
            return {"status": 404, "code": "not-found"}
        owner, state, version = row
        if owner != trusted_member_id:
            return {"status": 403, "code": "not-owner"}
        if version != expected_version:
            return {"status": 409, "code": "stale-version"}
        if state == "cancelled":
            return {"status": 200, "code": "already-cancelled", "version": version}
        connection.execute("""
            UPDATE reservations_v2 SET state = 'cancelled', version = version + 1
            WHERE reservation_id = ?
        """, (reservation_id,))
        return {"status": 200, "code": "cancelled", "version": version + 1}
