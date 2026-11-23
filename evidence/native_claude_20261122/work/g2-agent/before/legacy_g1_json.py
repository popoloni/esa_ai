"""Use a JSON payload behind the same public reservation
interface.
"""
from dataclasses import dataclass
from pathlib import Path
import json
import sqlite3


@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False


def init_db(path: str | Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS bookings_v2 ( booking_no
            INTEGER PRIMARY KEY , payload TEXT NOT NULL )
        """)
        connection.commit()
    finally:
        connection.close()


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    payload = {"trusted_member_id": trusted_member_id, "asset_id": asset_id,
               "starts_at": starts_at, "ends_at": ends_at,
               "idempotency_key": idempotency_key}
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.execute("INSERT INTO bookings_v2 (payload) VALUES (?)",
                                    (json.dumps(payload),))
        identifier = cursor.lastrowid
        connection.commit()
    finally:
        connection.close()
    return Outcome(201, "confirmed", identifier)


def get_reservation(path: str | Path, reservation_id: int) -> dict | None:
    connection = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        row = connection.execute("SELECT payload FROM bookings_v2 WHERE booking_no = ?",
                                 (reservation_id,)).fetchone()
    finally:
        connection.close()
    if row is None:
        return None
    return {"reservation_id": reservation_id, **json.loads(row[0])}
