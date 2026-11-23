# G2 decision record

## Expect

Contract: RES-001/v1 + G2-OD-01 + G2-OD-02 (docs/contract.md, docs/G2-OD-02.md). API unchanged: `init_db`, `reserve`, `get_reservation`; `Outcome` unchanged.
Outcome: validated (422), idempotent (200 replay / 409 key reused), conflict-checked (409), atomic reservations on schema v2, plus migration from three authorized legacy representations: the `reservations` table with `id,member_id,...,request_key`, the `bookings_v2` JSON table, and the retained AP-G1 `reservations` table with the public column names.

Acceptance example: a record created by `legacy_g1_recorded` (id 1, member-1/A/09:00-10:00/retained-key) is migrated by `init_db`. `get_reservation` returns the same id and values. `reserve` with the same request returns 200, id 1, replayed=True. A second `init_db` changes nothing. The same data with starts_at="bad" makes `init_db` raise ValueError and leaves the file bytes unchanged.

Open owner question: none blocking this increment. One item needs a mapping if wanted: a database created by the prior G1 candidate `prior/booking.py` has a different schema (`id` + `idempotency_key` columns). It is not an authorized source, so it is refused with ValueError and not guessed (see Limits).

## Delegate

Edited only `booking.py` and `DOSSIER.md`. Implemented schema v2 (`reservations_v2`, `PRAGMA user_version=2`, UNIQUE(member,key), SHA-256 fingerprint of asset/start/end). Writes use `BEGIN IMMEDIATE` so the replay/conflict check and the insert are one transaction. Migration runs in one transaction and leaves legacy tables untouched, so the original table survives as evidence.
Left unchanged: docs, tests, legacy_*.py, prior/, READER_ENTRY.json.

## Observe

- First run of `python -m unittest discover -s tests` against the retained G1 `booking.py`: 17 tests, failures=15, errors=2. This reproduced the missing behavior.
- After the first implementation: 17 tests, errors=2. Rows with an invalid field and a shared identity raised IntegrityError, but the tests expect ValueError.
- Correction: migration now checks per-row validity first, then duplicate identity (IntegrityError), then overlap (ValueError). Reason: the tests treat an invalid row as an owner-mapping refusal (ValueError), and duplicate identity as IntegrityError when the rows are otherwise valid.
- Final run: 17 tests, OK.
- Manual probe (`python -I`, scratchpad script): `init_db` twice on a fresh file works. Invalid-identifier, invalid-timestamp and invalid-interval return 422 with distinct codes. The sequence 201, replay 200 (replayed=True, same id), changed payload 409 `idempotency-key-reused` behaved as specified. A prior-candidate-schema database is refused with ValueError.
- sha256 of the three `legacy_g1*.py` files matches READER_ENTRY.json. `prior/booking.py` matches its recorded hash.

## Decide

Proposals and handoff scope:
- ACCEPT, as development evidence: the G2 behavior and the two supplied sources, plus the G2-OD-02 retained-column source.
- ASK: whether databases written by the prior candidate `prior/booking.py` (columns `id,...,idempotency_key`, no fingerprint) should be migrated. Nothing authorizes this, so it is refused.
- REJECT: guessing mappings, discarding rows, or inventing outcomes for invalid, duplicate, overlapping, dual or unknown legacy data.

Handoff: protected acceptance and continuation are for the operator. Human acceptance is not observed (READER_ENTRY.json says PENDING).

Limits:
- Only the supplied dev tests and my probe were run; no protected acceptance run.
- Concurrency is checked by one two-thread test on local SQLite. There is no distributed or crash-recovery claim.
- The overlap check compares ISO strings lexicographically. This is valid only because the timestamp format is fixed-width UTC.
- `reserve` and `get_reservation` do not auto-migrate. An unmigrated file gives sqlite3.OperationalError until `init_db` is called.
- The migrated table is named `reservations_v2`, and the legacy `reservations` table stays beside it. The archive name is my choice, and the tests do not prescribe one.
