# G1/I01 — agent plan and acceptance examples (pre-implementation)

Status: proposal only. Not implemented; storage not initialised; no checks run;
no owner response read. Examples marked **[pending Q#]** depend on an owner answer
in `AGENT_QUESTIONS.md` and must not be implemented until that answer exists.

## Acceptance examples (Given/When/Then)

**E1 — first confirmed reservation (from brief, G1-I01.md:32-35)**
Given an empty database initialised with `init_db(p)`,
When `reserve(p, trusted_member_id="member-1", asset_id="A",
starts_at="2025-05-14T09:00:00Z", ends_at="2025-05-14T10:00:00Z",
idempotency_key="key-1")` is called,
Then it returns `Outcome(status=201, code="confirmed", reservation_id=n, replayed=False)`
with `n` an `int` and `n > 0`.

**E2 — durable read from a new process**
Given E1 has returned and the writing process has exited,
When a separate Python process calls `get_reservation(p, n)`,
Then it returns a mapping with exactly the keys `reservation_id, trusted_member_id,
asset_id, starts_at, ends_at, idempotency_key`, and values `n, "member-1", "A",
"2025-05-14T09:00:00Z", "2025-05-14T10:00:00Z", "key-1"`.
(Observation probe, not a fifth test and not crash recovery — G1-I01.md:40-41.)

**E3 — safe SQL binding with quotes**
Given an empty initialised database,
When reserving with `trusted_member_id="o'brien\"; DROP TABLE x;--"` and
`asset_id="A'"` (both ≤128 chars),
Then the result is `201/confirmed` and `get_reservation` returns those strings exactly.

**E4 — read is side-effect free and fresh**
Given E1, When `get_reservation(p, n)` is called twice and the first result is mutated,
Then the second result still equals the original request, and the stored data is
unchanged.

**E5 — init_db preserves data**
Given E1, When `init_db(p)` is called again, Then `get_reservation(p, n)` still
returns the E2 mapping.

**E6 — unknown identifier [pending Q1]**
Given an initialised database with no reservation `999`,
When `get_reservation(p, 999)` is called,
Then: *owner decides* — either returns `None`, or raises `<named exception>`.

**E7 — missing storage on read [pending Q2]**
Given `p` does not exist, When `get_reservation(p, 1)` is called,
Then: *owner decides*; proposed: raises, and `p` still does not exist afterwards.

**E8 — storage failure propagates**
Given `p` points to an unwritable location or a non-SQLite file,
When `reserve` is called, Then an exception propagates; no `201/confirmed` Outcome
is returned.

## Implementation plan (after owner response only)

1. Read the dated owner response and the supplied acceptance checks.
2. Update `DOSSIER.md` with the agreed example(s), as the brief requires.
3. `init_db`: `sqlite3.connect`, `CREATE TABLE IF NOT EXISTS` one table
   (integer primary key + five TEXT columns, per ADR reference design).
4. `reserve`: parameterised `INSERT`, commit (connection context manager), return
   `Outcome(201, "confirmed", lastrowid, False)`; let exceptions propagate.
5. `get_reservation`: parameterised `SELECT`, build a fresh `dict`; missing-row and
   missing-file behavior exactly as answered for Q1/Q2.
6. Run the supplied public checks as feedback; report commands and outcomes.
   Leave the full-contract (RES-001/v1) diagnostic visible and failing as expected.

## Explicitly not done in this run

No edits to `booking.py`, `QUESTIONS.md`, `DOSSIER.md`, `docs/`, `READER_ENTRY.json`.
No database created, no tests run (none present), no owner answer requested.
