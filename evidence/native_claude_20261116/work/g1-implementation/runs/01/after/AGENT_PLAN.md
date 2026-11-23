# Agent plan (G1/I01) — draft, not started

Status: waiting for the owner answer to Q1 in `AGENT_QUESTIONS.md`. No implementation exists.

Intended steps once answered:
1. Read the dated owner response before touching `booking.py`.
2. Implement in `booking.py` only: SQLite file, one private table (integer primary key plus five text columns), parameterized SQL.
3. `init_db`: `CREATE TABLE IF NOT EXISTS`, which preserves existing data.
4. `reserve`: insert and commit before returning `Outcome(201, "confirmed", rowid, False)`. Don't catch storage errors.
5. `get_reservation`: read-only select, returning a fresh dict with the six public fields. Absent-id behavior follows the owner's answer.
6. Do not add validation, overlap, replay, fingerprints or transactions beyond a plain commit. Those are G2.
7. Run the public acceptance checks as feedback only, plus a separate-process read. Report actual commands and outcomes.

Out of scope: G2 behavior, `historical_tests/`, `docs/`, `READER_ENTRY.json`, and the learner's `QUESTIONS.md`.
