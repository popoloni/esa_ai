# G2 decision record

## Expect

Contract: RES-001/v1 + G2-OD-01 + G2-OD-02. API unchanged (`init_db`, `reserve`,
`get_reservation`, `Outcome`). Outcome: validated, idempotent, non-overlapping reservations
in schema v2, plus migration of three authorized G1 representations (columnar `reservations`
with `member_id/request_key`, `bookings_v2` JSON, and the retained AP-G1 columnar
`reservations` with public column names).

Acceptance example (discriminating): member-1 books asset A 09:00-10:00 with key `key-1` ->
201. Same request again -> 200, same ID, `replayed=True`, no new row. Same key with end
11:00 -> 409 `idempotency-key-reused`. Member-2 on A 09:30-10:30 -> 409 `interval-conflict`.
Member-2 on A 10:00-11:00 -> 201 (adjacency). A legacy retained-AP-G1 DB with one valid row
migrates, keeps its ID, and replays that ID; with `starts_at="bad"` it raises `ValueError`
and the file bytes are unchanged.

Open owner questions: none blocking this increment (see Decide for caveats).

## Delegate

Edited only `booking.py` (rewritten) and this file. Not touched: docs, tests, `prior/`,
`legacy_g1*.py`, `READER_ENTRY.json`.

Implementation choices (mine, not stated in the contract; please confirm):
- New table `reservations_v2` (with fingerprint, UNIQUE(member,key)), `PRAGMA user_version=2`.
  Legacy tables are left untouched as historical evidence.
- 422 codes: `invalid-identifier`, `invalid-timestamp`, `invalid-interval` (contract says
  "distinct" but gives no strings). Check order: identifiers, timestamps, interval.
  Exactly 24h is accepted ("at most").
- Refusals: duplicate identity -> `sqlite3.IntegrityError` (as the supplied test requires);
  invalid/overlapping rows, unknown/dual schema, unsupported version -> `ValueError`.
  When several defects coexist, per-row validity is reported first, then duplicates, then overlaps.
- `reserve` does not auto-migrate; on an unmigrated DB it raises `sqlite3.OperationalError`.

## Observe

- Baseline `python -m pytest -q tests` on the retained `booking.py`: 17 failed, 7 passed.
  The G1 code had no validation, replay, overlap or migration.
- After the rewrite, same command: 17 passed, 7 subtests passed (0.11s). This covers
  `ReservationFullAPI`, `ReservationMigration` and `RecordedG1Migration`.
- Extra probe (outside the repo, `python -I`): the six invalid inputs gave the expected distinct
  422 codes. Exactly 24h was accepted and 24h+1s rejected. 20 rounds of 8 threads on one slot
  each gave exactly one 201 and seven 409s. A DB created by `prior/booking.py` (`g1_reservation`)
  is refused with `ValueError`.
- Corrections made: none were needed after the first full run. The second line of the probe
  looked wrong, but it was my probe reusing a key after a valid 24h request, not a defect.
- Not run: the protected acceptance and continuation (operator's step).

## Decide

- G2-OD-01 migrations (columnar, JSON): ACCEPT, implemented and tested.
- G2-OD-02 retained public-column mapping: ACCEPT as instructed. Caveat: the document says
  the AI recording operator authored it and that it is not a live business-owner approval.
  I implemented it because the task names it as part of the contract, but human acceptance is
  still `PENDING` in `READER_ENTRY.json` and I have not observed any.
- The `g1_reservation` table written by `prior/booking.py` (the actual G1 module snapshot)
  is not among the authorized sources. It is refused, not guessed. If real data exists in that
  shape, an owner mapping is needed. G2-OD-02 describes the retained AP-G1 as the `reservations`
  columns, which differs from this snapshot, so the owner should confirm which is the real one.
- Handoff scope: local SQLite, tested in one process environment (threads). No
  distributed-system, crash-recovery or multi-process claim. A `legacy_g1` table and the new
  table coexist after migration, which is intended. Reinit is idempotent (checked by tests).
