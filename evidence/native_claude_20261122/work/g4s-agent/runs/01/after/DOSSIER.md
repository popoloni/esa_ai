# G4 decision record

## Expect

Contract OPS-G4/v3 (docs/contract.md, the only document supplied; no conflicts found). Outcome:
`diagnose(path)` observes existing G3 schema-3 storage read-only; `cost_summary(attempts, accepted)` divides total cost/time of all attempts by separately decided accepted outcomes.

Discriminating acceptance example: a database holding active rows 09:00-10:00 and 09:30-10:30 on asset A, plus a cancelled row and an adjacent 10:30-11:00 row, gives `ACTIVE_OVERLAP` with only the pair `[[1,2]]`, and file bytes are identical afterwards. `cost_summary` with failed 2.20 EUR/12 min plus accepted 0.80 EUR/8 min and accepted=1 gives 3.00 EUR and 20 min per outcome; accepted=0 gives null metrics and `NO_ACCEPTED_OUTCOME`.

Open owner question: none blocking. Assumption I made: schema version other than 3 is refused (the contract targets schema 3 only). The owner may confirm.

## Delegate

Only `operations.py` was edited (plus this file). Public names unchanged. Implemented:
- Exact full-column-signature match among reference `reservations`, recorded `reservations_v2` and native `reservations_v2`. Zero matches means refusal; two matches (competing current layouts) means refusal. A historical `reservations` table with another signature is ignored, not counted.
- Read-only SQLite URI (`mode=ro`), missing file raises FileNotFoundError without creation, SHA-256 of file bytes before and after; a difference raises RuntimeError rather than claiming a stable snapshot.
- Overlap is `a.start < b.end and b.start < a.end` on the same asset, active rows only (adjacency and cancelled excluded).
- Decimal cost/time sums; non-numeric, NaN/Infinity, negative, bool and missing fields raise ValueError; accepted must be a nonnegative int.

Corrections: the initial stubs raised NotImplementedError, so all 13 tests errored on the first run (reported 17 errors, counting subtests). No other corrections were needed.

## Observe

- `python3 -m unittest tests.test_g4` before the change: FAILED (errors=17).
- Same command after the change: Ran 13 tests, OK.
- Ad hoc scratch check (not part of the repo) of the recorded and native layouts with a coexisting historical `reservations` table: both gave `ACTIVE_OVERLAP`, overlap detected, the adjacent row not paired. Ids printed as None only because my scratch table had no primary key.

Limits: the concurrent-modification detector compares whole-file digests before and after, so it catches changes that completed between them and cannot prove a snapshot against a writer mid-read. Not exercised: a live concurrent writer, WAL-mode databases, malformed timestamps (these would raise ValueError from parsing), very large tables. Protected acceptance has not been run by me. No human approval has been observed; READER_ENTRY.json still says PENDING.

## Decide

- Proposal 1, read-only diagnosis of the three recognised layouts: ACCEPT at development level, pending the protected check.
- Proposal 2, all-attempt cost accounting with a null result at zero accepted: ACCEPT at development level.
- Proposal 3, any repair of overlapping rows or of an operational database: ASK. Nothing here authorizes it. The fictional operations lead owns that decision. Hypothesis supported: overlapping active rows exist in the synthetic fixtures. Still open: how they arose (concurrency vs. data corruption). Next observation: a diagnose run on a copy of the real storage, at near-zero cost.

Handoff scope: `operations.py` and `DOSSIER.md` only. Docs, tests, dependencies and READER_ENTRY.json were untouched.
