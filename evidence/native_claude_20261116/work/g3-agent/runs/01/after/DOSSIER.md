# G3 decision record

## Expect

Contract RES-002/v1 (docs/contract.md): schema version 3; G2 rows migrate to `active`/version 1 with
IDs and the six public fields unchanged; `get_reservation` keeps its six-field shape even for a cancelled
row; new `reservation_status(path,id)` -> `{state,version}` or `None`; new
`cancel(path,id,*,trusted_member_id,expected_version)` with 404/not-found, 403/not-owner, 409/stale-version
(no change), 200/cancelled (version +1 once), 200/already-cancelled (current cancelled version, no
increment); cancelled intervals stop blocking; replaying the original reserve request returns the original
identity and never revives the row.

Acceptance example: member-1 reserves A 09:00-10:00 (id 1, version 1). `cancel(id=1, member-1, expected_version=1)`
-> 200/cancelled, version 2. Repeat with 2 -> 200/already-cancelled, version 2. Repeat with 1 -> 409/stale-version.
member-2 can now reserve the same slot (201). Replaying member-1's original key returns id 1, replayed=True,
status still cancelled.

Open owner question (blocking for the supplied test): `tests/test_g3.py` builds its starting database with
`legacy_booking.init_db`, which writes `PRAGMA user_version=2` and a table `reservations` with seven
columns (id, asset_id, member_id, starts_at, ends_at, request_key, request_hash). That is neither a G2
`reservations_v2` database nor one of the exact column signatures authorized by G2-OD-01/G2-OD-02, and
`booking.init_db` deliberately rejects unknown signatures ("owner mapping required"). Should that shape be
an approved migration source (map by column name, drop request_hash, recompute the fingerprint)? I did not
add it, because that would be a new data-mapping policy.

## Delegate

Edited only `booking.py` and `DOSSIER.md`. Changes in `booking.py`:
- `SCHEMA_VERSION = 3`; table `reservations_v2` gains `state` (active/cancelled, CHECK) and `version`
  (default 1). Table name kept so the public data location is unchanged.
- `init_db`: new v2 -> v3 branch (ALTER TABLE x2 + user_version, inside the existing BEGIN IMMEDIATE
  transaction, rolled back on error); v0 legacy migration and v3 re-run unchanged in behavior.
- `reserve`: interval-conflict check now counts only `state='active'` rows; idempotency lookup still
  matches any state, so a replay returns the original identity and does not revive.
- `reservation_status`: read-only (`mode=ro`) lookup.
- `cancel`: one `BEGIN IMMEDIATE` transaction does the check and the update. Check order: missing, owner,
  version, already-cancelled, transition. Owner is checked before version so a non-owner learns nothing
  about the version; non-200 results carry `version: None`. (Order is my choice where the contract lists
  outcomes without ranking them; please confirm.)
- Not touched: `get_reservation`, `Outcome`, docs, tests, `legacy_booking.py`, `prior/`, `READER_ENTRY.json`.

## Observe

1. `python3 -m unittest tests.test_g3` before edits: 7 errors, all in `setUp` at `booking.init_db`
   ("schema version 2 marker without reservation table").
2. Same command after edits: 7 errors, now `ValueError: unsupported schema version 2`, still in `setUp`.
   **The supplied development check does not pass (0/7 run past setUp).** The cause is the fixture shape
   in the open question above, not the new cancel/status code, which these tests never reached.
3. Own scratch check (outside the workspace, not part of the deliverable) using a real G2 database made
   by `prior/booking.py`, then migrated by the new `booking.init_db` (run twice): record unchanged
   (six fields); status `{active, 1}`, unknown id -> None; 404, 403, 409 as specified; active slot
   conflicts (409/interval-conflict); cancel -> 200/cancelled v2; repeat with 2 -> 200/already-cancelled
   v2; old version 1 -> 409; history record identical; new member reserves the slot (201); original
   replay -> id 1, replayed=True, state cancelled v2. All matched the contract.

## Decide

- Increment implemented and observed for G2-produced databases: ACCEPT as an implementation proposal,
  pending the operator's protected acceptance.
- Migration of the `legacy_booking` v2 seven-column shape: ASK (owner decision needed; not implemented).
- Owner-before-version check order: ASK to confirm (contract is silent on precedence).
- The task mentions "three proposals", but none are in docs/ or the workspace, so I could not rule on
  them individually.

Limits: no human approval observed. Not tested: concurrent cancels (atomicity relies on SQLite
`BEGIN IMMEDIATE`, reasoned but unexercised), refunds/deletion/staff override (out of contract), and
non-int `expected_version` (contract assumes valid typed arguments). About 12 tool commands used.
