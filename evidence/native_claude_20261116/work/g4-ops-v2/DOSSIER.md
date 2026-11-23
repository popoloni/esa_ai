# G4 decision record

## Expect

Contract OPS-G4/v2 (docs/contract.md): `diagnose(path)` is a read-only observation of the two
documented schema-3 representations; `cost_summary(attempts, accepted)` divides all attempt
cost/time by separately decided accepted outcomes.

Acceptance example: a DB with active rows 1 (09:00-10:00) and 2 (09:30-10:30) on asset A gives
`ACTIVE_OVERLAP` with pairs `[[1,2]]`, file bytes unchanged. `cost_summary` with 2.20 + 0.80 EUR,
1 accepted gives `3.00`; with 0 accepted gives null unit metrics and `NO_ACCEPTED_OUTCOME`.

**Open owner question (blocking, ASK):** the retained G3 candidate `booking.py` (identical to
`prior/booking.py`) creates `reservations_v2` with columns
`id, trusted_member_id, asset_id, starts_at, ends_at, idempotency_key, fingerprint, state, version`.
That matches neither contract signature (reference: `id, asset_id, member_id, ..., request_key,
request_hash, ...`; recorded: `reservation_id, ..., payload_fingerprint, ...`). The contract says to
refuse unsupported representations and not to guess a mapping. Should the owner add this third
signature (id column `id`, fingerprint column `fingerprint`), or is the contract text or the
candidate wrong? `g4_fixture.insert_overlap` also cannot target this table, since it writes
`payload_fingerprint`. I did not invent that mapping.

## Delegate

Edited only `operations.py` and `DOSSIER.md`. Implemented both functions per contract:
- `diagnose`: refuses missing path (no creation), opens via SQLite `mode=ro`, requires
  `user_version == 3` AND an exact column signature match for exactly one of the two documented
  tables; zero or two matches raise `ValueError`. Counts by state, strict-inequality overlap
  among active rows on the same asset (cancelled and adjacent excluded), sha256 of file bytes before and
  after; a change raises `RuntimeError`.
- `cost_summary`: Decimal sums; non-numeric, NaN/Infinity, negative, bool, or missing values raise
  `ValueError`; `accepted` must be a nonnegative int; zero accepted gives null metrics and `NO_ACCEPTED_OUTCOME`.

## Observe

- `python -m unittest tests.test_g4`: 11 tests, 3 errors. All other tests pass, including the reference
  schema, unknown-schema refusal, and every cost test.
- The 3 errors (clean storage, active overlap, cancelled row) all come from `ValueError: no supported
  current reservation representation found`. The tests build their DB with the retained `booking.init_db`,
  whose table has the unmapped signature above. The refusal is what the contract requires, so I did not
  loosen it to make the tests pass.
- Not verified: the overlap check compares ISO-8601 strings lexically (valid only for the uniform `...Z`
  format used here). Concurrent-modification detection compares before/after digests only and can miss
  a change that is made and then reverted. A pure-read digest does not prove no writer ran between the two reads.
  No test exercises it.

## Decide

- Cost accounting (all attempts over accepted outcomes): ACCEPT, passes development checks.
- Read-only diagnosis for the reference schema: ACCEPT as developed. For the retained candidate
  table: ASK. Do not accept until the owner states the mapping.
- Handoff: not ready for protected acceptance; 3 development checks fail pending the owner decision.
  No repair of any database is proposed or authorized here. Authorization for repair belongs to the
  operations lead.
