# G1 working note

Scope: G1/I01 first durable reservation and public read; final RES-001/v1 remains separate.

## Expected behavior before coding

Given an empty database, member `member-1`, asset `A`, 2025-05-14T09:00:00Z to
2025-05-14T10:00:00Z, key `key-1`: when the member reserves, the outcome is 201/confirmed,
a positive identifier, replayed False. When a separate process calls `get_reservation`
with that identifier, it returns exactly the six public fields with the request values.
Resolved by G1-OD-01: an absent identifier in an initialized database returns `None`; a
nonexistent database path raises `sqlite3.OperationalError` and creates no file (read-only URI).

## Proposal review

No proposals were supplied to this run. `AGENT_PLAN.md` / `AGENT_QUESTIONS.md` were read as
data; their Q1 is answered by G1-OD-01 (their other questions were not needed and no new policy was invented).

## Change and attempts

Reason: `booking.py` was an unimplemented stub. Implemented `init_db` (CREATE TABLE IF NOT EXISTS,
private table `g1_reservation`), `reserve` (parameterized INSERT, committed before returning
201/confirmed, errors propagate) and `get_reservation` (`mode=ro` URI via `Path.resolve().as_uri()`,
fresh dict, `None` when absent). Only `booking.py` and `DOSSIER.md` edited. A first write attempt
was blocked by a tool check before running; I re-ran it and confirmed the stub was unchanged.
No receipt files produced.

Commands and observations (development feedback only, not acceptance):
- `python3 -m unittest tests.test_g1_slice tests.test_g1_readonly`: 6 tests OK (stub: 6 errors).
- `python3 -m unittest tests.test_g1_full_api`: 10 run, 3 pass, 7 fail (G2: overlap, replay,
  changed key, validation, concurrency). Expected; left visible.
- `python3 -m unittest historical_tests.test_booking`: 10 run, 7 failures, 3 errors; it counts
  the original `reservations` table and per ADR 0001 does not gate G1.
- Separate-process probe: reserve gave 201/confirmed id 1; a new process read all six fields
  equal to the request; id 2 gave `None`; missing path gave `OperationalError`, no file created.

## Handoff

Passed: the G1 public checks above. Remaining: all G2 behavior (validation, overlap, replay,
fingerprinting, atomic check-and-insert); concurrent `reserve` calls on one DB are not
coordinated beyond SQLite defaults. Not tested: crash recovery, corrupt/unwritable storage,
non-integer or non-positive ids beyond `-1`/`-77` returning `None`. No human approval was
observed; the operator decides on protected acceptance and continuation.
