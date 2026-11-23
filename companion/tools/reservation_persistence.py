#!/usr/bin/env python3
"""Write, exit, then read through the retained candidate's public API.

No table or column names are part of this probe. A normal process exit does
not establish crash recovery or prove that arbitrary hostile code is safe.
"""
import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["write", "read"])
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--reservation-id", type=int)
    args = parser.parse_args()
    database = args.database.resolve()
    sys.path.insert(0, str(args.candidate.resolve()))
    booking = importlib.import_module("booking")
    if args.stage == "write":
        if database.exists():
            parser.error("A persistence demonstration needs a fresh database.")
        booking.init_db(database)
        request = {"trusted_member_id": "member-1", "asset_id": "A",
                   "starts_at": "2026-11-02T09:00:00Z", "ends_at": "2026-11-02T10:00:00Z",
                   "idempotency_key": "g1-durable-1"}
        result = asdict(booking.reserve(database, **request))
        assert (result["status"], result["code"]) == (201, "confirmed")
        assert isinstance(result["reservation_id"], int) and result["reservation_id"] > 0
        data = {"status": "FIRST_WRITE_COMPLETED", "request": request, "outcome": result}
    else:
        if args.reservation_id is None or not database.is_file():
            parser.error("The read stage requires the writer's database and returned reservation identifier.")
        record = booking.get_reservation(database, args.reservation_id)
        data = {"status": "PUBLIC_RECORD_REOPENED" if record is not None else "PUBLIC_RECORD_MISSING",
                "reservation": record, "public_api": "get_reservation(path, reservation_id)"}
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
