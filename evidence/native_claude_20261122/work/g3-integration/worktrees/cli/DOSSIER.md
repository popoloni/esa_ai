# G3 decision record

## Expect

Contract RES-002/v1 (docs/contract.md): schema 3; G2 rows migrate to `active`/version 1 with IDs and public fields unchanged; `get_reservation` keeps its six fields (also for cancelled rows); new `reservation_status(path, id)` -> `{state, version}` or None; new `cancel(path, id, *, trusted_member_id, expected_version)` with 404 not-found / 403 not-owner / 409 stale-version (no change), 200 cancelled (version +1), 200 already-cancelled (current cancelled version, no increment). Cancelled intervals stop blocking; replaying the original `reserve` returns the original ID and does not revive the row.

Acceptance example: member-1 reserves A 09:00-10:00 (id 1, v1). `cancel(..., "member-1", 1)` -> 200 cancelled v2. `cancel(..., "member-1", 1)` -> 409 stale-version; `cancel(..., "member-1", 2)` -> 200 already-cancelled v2. member-2 can now reserve the same slot (201). Replaying member-1's original request returns id 1 replayed, status stays `cancelled`.

Open owner question (not blocking, not decided by me): the contract does not specify the response for a cancel with a non-integer/bool `expected_version` (it says typed arguments are assumed), and 403/404/409 results omit `version` (my choice, to avoid leaking state to non-owners). Refunds, physical deletion and staff overrides are out of scope per contract.

## Delegate

Only `booking.py` and this file were edited. New table `reservations_v3` (state, version columns) plus `user_version = 3`; older tables (`reservations_v2`, legacy G1 tables, the `reservations` table written by `legacy_booking.py`) are never modified or dropped. `init_db` now migrates: version 0 legacy G1 layouts (as before, into v3), version 2 (`reservations_v2` from the G2 candidate, or the exact `reservations` layout written by `legacy_booking.py`) and version 3 (idempotent). Ambiguous or unknown version-2 layouts are refused with an owner-mapping error.

## Observe

- Baseline `python -m pytest -q tests`: 7 failed. Cause observed: `init_db` rejected a `legacy_booking.py` database (user_version 2, table `reservations` without `reservations_v2`) with "schema version 2 without reservations_v2", and the new API stubs raised NotImplementedError.
- After the change `python -m pytest -q tests`: 7 passed.
- Ad hoc script (not a supplied check): a DB made by `prior/booking.py` (G2 candidate) migrates; `get_reservation` equals the pre-migration record, status `{active, 1}`, second `init_db` is a no-op, wrong owner -> 403, owner -> 200 cancelled v2, stale -> 409; `reservations_v2` is retained, user_version 3.
- `legacy_booking.py` and `prior/booking.py` hashes match READER_ENTRY.json (checked by sha256sum).

Corrections, explained: (1) migration source widened to the `legacy_booking.py` layout because the supplied test fixture uses it as "G2 rows"; the field mapping is one-to-one, so no new policy was invented. (2) The conflict query now filters `state = 'active'` so cancelled slots are released; the idempotency lookup is deliberately state-independent so replays cannot revive or re-create. (3) Fingerprints are recomputed with this module's formula during migration, since the legacy hash uses a different JSON serialisation.

## Decide

ACCEPT is not mine to give: human acceptance stays PENDING and protected acceptance/continuation were not run. Proposals: ACCEPT the status/cancel implementation as meeting the visible checks; ACCEPT migrating both schema-2 layouts as consistent with the contract's "existing G2 rows"; ASK the owner about the typed-argument edge case and whether non-success results should carry `version`. Limits: no concurrency/multi-process test was run (atomicity relies on `BEGIN IMMEDIATE`); no data-bearing migration of overlapping or invalid schema-2 rows is validated; docs, tests, prior snapshots and READER_ENTRY.json were not touched.
