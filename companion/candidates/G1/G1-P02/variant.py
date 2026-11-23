"""Proposal using one local registry behind the public
interface.
"""
from dataclasses import dataclass
from pathlib import Path
import sqlite3

@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False

_records = {}
def init_db(path):
    sqlite3.connect(path).close()
    _records.setdefault(str(path), {})
def reserve(path, **request):
    identifier = len(_records.setdefault(str(path), {})) + 1
    _records[str(path)][identifier] = {"reservation_id": identifier, **request}
    return Outcome(201, "confirmed", identifier)
def get_reservation(path, reservation_id):
    if not Path(path).exists():
        raise sqlite3.OperationalError("storage does not exist")
    row = _records.get(str(path), {}).get(reservation_id)
    return dict(row) if row is not None else None
