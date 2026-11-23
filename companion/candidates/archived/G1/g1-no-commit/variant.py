"""Constructed teaching variant; no model run is represented."""
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False


def init_db(path: str | Path) -> None:
    with closing(sqlite3.connect(path)) as con, con:
        con.execute("""CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            member_id TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            starts_at TEXT NOT NULL,
            ends_at TEXT NOT NULL,
            request_key TEXT NOT NULL
        )""")


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    with closing(sqlite3.connect(db_path)) as con:
        cursor = con.execute("""
            INSERT INTO reservations
            (member_id, asset_id, starts_at, ends_at, request_key)
            VALUES (?, ?, ?, ?, ?)
        """, (trusted_member_id, asset_id, starts_at, ends_at, idempotency_key))
        reservation_id = cursor.lastrowid
    return Outcome(201, "confirmed", reservation_id)


def get_reservation(path: str | Path, reservation_id: int) -> dict | None:
    with closing(sqlite3.connect(path)) as con:
        row = con.execute("""
            SELECT id, member_id, asset_id, starts_at, ends_at, request_key
            FROM reservations WHERE id = ?
        """, (reservation_id,)).fetchone()
    if row is None:
        return None
    return dict(zip(("reservation_id", "trusted_member_id", "asset_id",
                     "starts_at", "ends_at", "idempotency_key"), row))
