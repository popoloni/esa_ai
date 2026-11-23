# G4 decision record

## Expect

Contract OPS-G4/v3 (docs/contract.md, the only document in docs). Outcome: `diagnose(path)` observes
schema-3 storage read-only and `cost_summary(attempts, accepted)` accounts all attempts against
separately supplied accepted outcomes.

Acceptance example: a reference-layout database with rows 1 and 2 active on asset A, 09:00-10:00 and
09:30-10:30, gives `ACTIVE_OVERLAP`, pairs `[[1,2]]`, and identical bytes afterwards. Costs
`2.20/12 min` and `0.80/8 min` with 1 accepted give `3.00` EUR and `20` min per accepted outcome; with
0 accepted the unit metrics are null and the status is `NO_ACCEPTED_OUTCOME`.

**Open owner question (blocking, not guessed).** The retained G3 `booking.py` (identical to
`prior/booking.py`) creates table `reservations_v3` with the native column list plus `user_version=3`.
v3 names only `reservations` (reference) and `reservations_v2` (recorded or native). Under v3 the name
`reservations_v3` is unsupported, so `diagnose()` refuses it. Should the owner extend the contract to
accept `reservations_v3` with the native signature (id column `id`)? `g4_fixture.insert_overlap`
also does not know that table, and fixtures are not in my edit scope.

## Delegate

Edited only `operations.py` and `DOSSIER.md`. `diagnose` opens SQLite with `mode=ro`, requires
`user_version == 3` (my reading of "targets schema 3"), matches full signatures, refuses none or
competing matches, and compares sha256/size/mtime before and after, raising `RuntimeError` on
change. It excludes cancelled rows and adjacency. `cost_summary` uses Decimal, rejects bool,
nonnumeric, nonfinite and negative values with `ValueError`, and rejects a bad `accepted` count. No
repair, initialization or other file was touched.

## Observe

- Baseline `python -m unittest tests.test_g4`: 13 tests, 17 errors, all `NotImplementedError` plus one
  fixture `ValueError`.
- After implementation, same command: 13 tests, **10 pass, 3 error**. Failing:
  `test_clean_storage_is_observed_without_mutation`, `test_active_overlap_is_detected_not_repaired`
  and `test_cancelled_row_does_not_create_false_alarm`. Each builds its database with
  `booking.init_db`, which yields `reservations_v3`, so refusal is the contract-conformant result.
  I did not widen the mapping to turn them green.
- Not exercised: a positive diagnosis of the native `reservations_v2` layout (no passing test covers
  it), and the concurrent-modification branch. Both are untested code paths.
- No test or protected file was modified. The first shell attempt to write `operations.py` was
  blocked by the tool's command filter, so I wrote it with the file-edit tool instead.

## Decide

- Cost accounting: ACCEPT (all attempts in numerator, zero accepted yields null metrics).
- Diagnosis for the three named layouts: ACCEPT as implemented, with the untested native path noted.
- `reservations_v3` support: ASK. Only the owner can approve this mapping. Until then three development
  checks fail by design. Handoff scope: `operations.py` and `DOSSIER.md` only; protected acceptance and
  continuation are the operator's to run. A clean local check is not permission to change an operational
  database nor evidence of product-level reliability. No hypothesis about the corrupted fixtures can be
  stated as supported yet because no fixture has been diagnosed on the actual G3 table.
