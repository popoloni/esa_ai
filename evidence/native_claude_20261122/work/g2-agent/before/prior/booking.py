"""G1/I01 public interface: first durable reservation and public read.

Scope is deliberately limited (docs/G1-I01.md, docs/G1-OD-01.md). Validation,
overlap, replay, changed-key handling and atomic check-and-insert are G2.
"""
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

_FIELDS = ("trusted_member_id", "asset_id", "starts_at", "ends_at",
           "idempotency_key")


@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False


def init_db(path: str | Path) -> None:
    # CREATE TABLE IF NOT EXISTS preserves existing data. Schema is private.
    with closing(sqlite3.connect(path)) as conn:
        with conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS reservations ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "trusted_member_id TEXT NOT NULL, asset_id TEXT NOT NULL, "
                "starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, "
                "idempotency_key TEXT NOT NULL)")


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    values = (trusted_member_id, asset_id, starts_at, ends_at, idempotency_key)
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:  # commits on success, rolls back on error
            cursor = conn.execute(
                "INSERT INTO reservations (trusted_member_id, asset_id, "
                "starts_at, ends_at, idempotency_key) VALUES (?, ?, ?, ?, ?)",
                values)
            reservation_id = cursor.lastrowid
    # Reached only after the commit; storage errors propagate unchanged.
    return Outcome(201, "confirmed", reservation_id, False)


def get_reservation(path: str | Path, reservation_id: int):
    # G1-OD-01: read-only URI; a missing file raises sqlite3.OperationalError
    # and is not created. Path.as_uri() encodes spaces, '?' and '#'.
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        row = conn.execute(
            "SELECT id, trusted_member_id, asset_id, starts_at, ends_at, "
            "idempotency_key FROM reservations WHERE id = ?",
            (reservation_id,)).fetchone()
    if row is None:
        return None
    return {"reservation_id": row[0], **dict(zip(_FIELDS, row[1:]))}
