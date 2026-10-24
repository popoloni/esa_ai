"""First greenfield attempt. Implement from docs/contract.md before reading reference.

The caller supplies trusted_member_id from a hypothetical authenticated layer.
This exercise does not implement authentication or an HTTP server.
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
    """Create durable storage according to the reviewed contract."""
    raise NotImplementedError('Design storage and its invariants first')


def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    """Implement a single atomic check-and-insert; return a structured result."""
    raise NotImplementedError('Derive behavior from the contract and tests')
