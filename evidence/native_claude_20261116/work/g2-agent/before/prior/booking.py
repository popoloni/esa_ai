"""G1/I01 public interface: first durable reservation and public read.

Validation, overlap, replay, fingerprints and atomic check-and-insert are G2.
"""
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False


_SCHEMA = """CREATE TABLE IF NOT EXISTS g1_reservation (
    id INTEGER PRIMARY KEY,
    trusted_member_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    idempotency_key TEXT NOT NULL)"""


def init_db(path: str | Path) -> None:
    with closing(sqlite3.connect(path)) as conn:
        with conn:
            conn.execute(_SCHEMA)


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:  # commits before we return; rolls back and re-raises on error
            cur = conn.execute(
                "INSERT INTO g1_reservation (trusted_member_id, asset_id, starts_at,"
                " ends_at, idempotency_key) VALUES (?, ?, ?, ?, ?)",
                (trusted_member_id, asset_id, starts_at, ends_at, idempotency_key))
            rid = cur.lastrowid
    return Outcome(201, "confirmed", rid, False)


def get_reservation(path: str | Path, reservation_id: int):
    # Missing file -> sqlite3.OperationalError; mode=ro never creates or mutates.
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        row = conn.execute(
            "SELECT id, trusted_member_id, asset_id, starts_at, ends_at,"
            " idempotency_key FROM g1_reservation WHERE id = ?",
            (reservation_id,)).fetchone()
    if row is None:
        return None
    keys = ("reservation_id", "trusted_member_id", "asset_id", "starts_at",
            "ends_at", "idempotency_key")
    return dict(zip(keys, row))
