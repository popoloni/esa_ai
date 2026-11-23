# G4 decision record

## Expect

Contract: OPS-G4/v3 (`docs/contract.md`) extended by G4-OD-01 (`docs/G4-OD-01.md`,
`docs/G4-SCHEMA-MAP.json`). Read both and AGENTS.md; I found no conflict. `booking.py`
SHA-256 matches the owner-recorded value (`c0b3857d...bbb887`), and `booking.py` matches `prior/booking.py`.

Outcome: `diagnose(path)` reads existing G3 schema-3 storage read-only and reports counts,
overlapping active pairs, schema version, resolved path and before/after digests.
`cost_summary(attempts, accepted)` divides all attempt cost and time by separately supplied accepted outcomes.

Acceptance example: a `booking.init_db` database (table `reservations_v3`) with active row 1 plus an
inserted active overlap row 2 on asset A gives `ACTIVE_OVERLAP`, pairs `[[1,2]]`, file bytes unchanged.
A cancelled row does not trigger that. `reservations_v3` with any other column list, or beside the
`reservations` table, is refused with `ValueError`.

Open owner question: none for this increment. G4-OD-01 covers only this booking.py hash;
any storage change needs a new owner decision. The decision is a supplied teaching response, not evidence that a human reviewed real storage.

## Delegate

Only `operations.py` (previously two `NotImplementedError` stubs) and this file were edited.
- `diagnose`: refuses a missing path (no creation), opens with SQLite `mode=ro`, requires `user_version==3`,
  matches the complete signature of four representations (reference, recorded v2, native v2, plus the mapped table
  read from `docs/G4-SCHEMA-MAP.json` when present). Zero matches or more than one raises `ValueError`.
  Overlap is `a.start < b.end and b.start < a.end` for active rows on the same asset (adjacency and cancelled rows excluded).
  Digest is taken before and after; a mismatch raises `RuntimeError` instead of claiming a stable snapshot.
- `cost_summary`: Decimal sums over all attempts; non-numeric, bool, None, NaN, Infinity and negative values raise `ValueError`;
  zero accepted gives null unit metrics and `NO_ACCEPTED_OUTCOME`.
- Not changed: tests, docs, `booking.py`, fixtures, `prior/`, `READER_ENTRY.json`.

## Observe

- First run of `python -m unittest discover -s tests` with the stubs: 13 tests, FAILED (errors=17), since nothing was implemented.
- Same command after implementing: 13 tests, OK.
- Extra probe (scratchpad script, not part of the repo): `reservations_v3` with wrong columns is refused;
  `reservations` + mapped `reservations_v3` is refused as competing; a fresh `init_db` file diagnoses cleanly
  with equal digests; "abc", None, True, "-0.1" are refused for cost.
- Observation worth knowing: `"1e999"` is accepted as a finite Decimal, as is any finite exponent notation.
  The contract does not say to refuse it, so I did not add a policy.
- No concurrent-writer test was run. The detection compares file digests before and after, so a change that is
  reverted between the two reads would go unnoticed, and WAL-mode sidecar files are not hashed.
- Not observed: the protected acceptance, and any real database. I did not use the network or install anything.
  No human approval was observed.

## Decide

- ACCEPT for the current increment: implementation in `operations.py` per the contract and G4-OD-01, passing the supplied tests.
- REJECT: guessing mappings for other schemas, repair or initialization of data, and treating a clean local check as proof of product reliability.
- ASK (owner): any change to `booking.py`/storage, and who may authorize repair of a database found with overlaps.
- The brief's "three proposals" are not defined in the supplied files, so I make no per-proposal decision.
- Handoff scope: the operator runs protected acceptance and continuation separately; this record does not claim their results.
