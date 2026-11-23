# G4 decision record

## Expect

Contract OPS-G4/v3 (docs/contract.md): `diagnose(path)` is a read-only observation of the three
documented schema-3 representations; `cost_summary(attempts, accepted)` divides all attempt
cost/time by separately decided accepted outcomes.

Acceptance example: a DB with active rows 1 (09:00-10:00) and 2 (09:30-10:30) on asset A gives
`ACTIVE_OVERLAP` with pairs `[[1,2]]`, file bytes unchanged. `cost_summary` with 2.20 + 0.80 EUR,
1 accepted gives `3.00`; with 0 accepted gives null unit metrics and `NO_ACCEPTED_OUTCOME`.

**Previously blocking question: resolved by contract OPS-G4/v3.** The native `reservations_v2` signature
(`id, trusted_member_id, asset_id, starts_at, ends_at, idempotency_key, fingerprint, state, version`),
which the retained `booking.py` creates, is now explicitly documented with id column `id`. I added exactly
that mapping and nothing else. `g4_fixture.insert_overlap` already supports it.

## Delegate

Edited only `operations.py` and `DOSSIER.md`.
- `diagnose` recognises three signatures: reference `reservations`, recorded `reservations_v2`
  (`reservation_id`), native `reservations_v2` (`id`). If a `reservations_v2` table exists it is the
  current one and must match recorded or native exactly, otherwise it is refused. An original
  `reservations` table beside it is historical: not counted, and not used as a fallback. Without
  `reservations_v2`, `reservations` must match the reference signature. `user_version == 3` is still
  required. It opens with `mode=ro`, never creates a missing path, excludes cancelled rows and adjacency,
  and compares sha256 before/after (a change raises `RuntimeError`).
- Correction reason: the earlier code refused the native table, which caused the 3 errors in the previous run.
- `cost_summary` is unchanged: Decimal sums; non-numeric, non-finite, negative, bool or missing values raise
  `ValueError`; zero accepted gives null metrics and `NO_ACCEPTED_OUTCOME`.

## Observe

- `python -m unittest tests.test_g4`: 11 tests, all OK (previously 3 errors).
- Ad hoc check (not part of the supplied tests): native DB plus `insert_overlap` gives `ACTIVE_OVERLAP`,
  pairs `[[1,2]]`. Adding a historical `reservations` table with an active row on the same asset did not
  change the pairs. A `reservations_v2` with an unrelated signature was refused.
- Not verified: no test covers a recorded-signature `reservations_v2` DB (only the code path is written).
  Overlap compares ISO-8601 strings lexically (valid only for uniform `...Z`). Concurrent-modification
  detection compares before/after digests only and misses a change that is made and reverted; no test
  exercises it. The contract does not define "competing representations" beyond these cases; I refuse when
  the current table does not match exactly one signature.
- `git status` at the parent level shows modified files outside this workspace (companion/, missions/).
  I did not touch them.

## Decide

- Cost accounting: ACCEPT on development checks.
- Read-only diagnosis for the three documented schema-3 representations: ACCEPT on development checks only.
  This is a teaching-case adapter, not a certification of arbitrary schema-3 databases, and a clean local
  check is not evidence of product-level reliability.
- Handoff: ready for the operator's protected acceptance, which I have not run. No repair of any database
  is proposed or authorized; authorization for repair belongs to the operations lead.
