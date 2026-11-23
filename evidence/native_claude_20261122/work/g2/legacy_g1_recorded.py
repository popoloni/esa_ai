"""The completed G1/I01 durable reservation and public read interface."""
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
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reservations (
                    reservation_id INTEGER PRIMARY KEY,
                    trusted_member_id TEXT NOT NULL,
                    asset_id TEXT NOT NULL,
                    starts_at TEXT NOT NULL,
                    ends_at TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL
                )
                """
            )


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    with closing(sqlite3.connect(db_path)) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO reservations (
                    trusted_member_id, asset_id, starts_at, ends_at,
                    idempotency_key
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (trusted_member_id, asset_id, starts_at, ends_at,
                 idempotency_key),
            )
            reservation_id = cursor.lastrowid

    return Outcome(
        status=201,
        code="confirmed",
        reservation_id=reservation_id,
        replayed=False,
    )


def get_reservation(path: str | Path, reservation_id: int):
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT reservation_id, trusted_member_id, asset_id, starts_at,
                   ends_at, idempotency_key
            FROM reservations
            WHERE reservation_id = ?
            """,
            (reservation_id,),
        ).fetchone()

    return None if row is None else dict(row)
