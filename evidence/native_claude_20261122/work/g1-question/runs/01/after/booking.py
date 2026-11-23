"""Implement the G1/I01 public interface; read docs/G1-I01.md
first.
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Outcome:
    status: int
    code: str
    reservation_id: int | None = None
    replayed: bool = False


def init_db(path: str | Path) -> None:
    raise NotImplementedError("Create the minimal durable storage")


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    raise NotImplementedError("Commit the first valid reservation before confirming")


def get_reservation(path: str | Path, reservation_id: int):
    raise NotImplementedError("Implement the agreed public read behavior")
