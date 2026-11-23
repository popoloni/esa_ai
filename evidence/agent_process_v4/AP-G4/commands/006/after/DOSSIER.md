# G4 decision record

## Expect

OPS-G4/v2 authorizes read-only diagnosis of exactly the documented schema-3
`reservations` and `reservations_v2` representations, plus accepted-outcome
accounting. Diagnosis must not count preserved source tables, change source
bytes, initialize missing storage, or infer a mapping from user_version alone.

Acceptance examples derived before coding:

- A single active reservation gives counts {"active": 1}, no overlap pairs, and
  NO_ACTIVE_OVERLAP_OBSERVED; before and after source digests agree.
- The supplied synthetic overlap gives pair [1, 2] in each supported layout.
  Cancelled rows and adjacent half-open intervals do not produce overlap pairs.
- The recorded current table may coexist with retained G1/G2 source tables.
  Those historical rows must not enter counts or overlap pairs. Two current
  layouts, an incomplete signature, or an unknown representation are refused.
- Missing storage is not created. A detected source or sidecar change during
  observation invalidates the result instead of being reported as stable.
- Illustrative attempts EUR 2.20 / 12 minutes and EUR 0.80 / 8 minutes,
  including a failed attempt, total EUR 3.00 / 20 minutes. With one separately
  accepted outcome the same totals are the unit metrics.
- With zero accepted outcomes, both unit metrics are null and status is
  NO_ACCEPTED_OUTCOME. Malformed text, nonfinite values, and negative values in
  either field raise ValueError.

Open owner decisions: any new/competing schema mapping; whether a reported
overlap merits a repair and the approved repair procedure; the independently
accepted outcome count; the actual euro/time budget for further observation.
None blocks this implementation of the two expressly authorized layouts.
An accepted count is a nonnegative integer, with booleans rejected; it is not
inferred from attempt status or limited to the number of attempts.

## Delegate

Only operations.py and DOSSIER.md may change. Preserve booking.py,
reservation_report.py, reservation_cli.py, reference_g3.py, g4_fixture.py,
the supplied tests, instructions, and every inherited dependency.
No repair, restoration, operational action, network access, or external package.
Work uses the required recorder and a budget of 40 commands / 45 seconds each.
The operator is AI; no human learner result or unverified model identity is claimed.

Implementation plan: match complete ordered column signatures and reject
unmapped tables; query a private disposable copy so even WAL shared-memory
activity cannot write the observed storage; compare source bytes and file
identity/metadata before and after. All accounting values are validated and
included, with Decimal totals and separately supplied accepted outcomes.

## Observe

- AP-G4/001 enumerated the supplied workspace without edits.
- AP-G4/002 read AGENTS.md, the complete contract, and the initial dossier.
- AP-G4/003 read the retained public implementation, report/CLI adapters,
  operations stubs, supplied fixture, and all supplied G4 development tests.
- AP-G4/004 read reference_g3.py, an explicit dependency of the supplied G4
  reference-layout test.
- AP-G4/005: `python3 -B -m unittest discover -s tests -v` ran 11 tests in
  0.019 seconds and failed with 15 error reports (including subtests), all
  NotImplementedError from the two operations stubs. No files changed.
- AP-G4/006 records these expectations and owner decisions before coding.

These are development receipts, not independent acceptance.

## Decide

ACCEPT the bounded implementation experiment for the two supplied mappings and
the specified accounting rules. REJECT any proposal to repair, restore, or
initialize the observed source as part of diagnosis. ASK the fictional
operations lead for a new mapping or repair authority when one is needed.

Supported now: missing operations behavior is reproduced. Open until observation:
whether the implementation satisfies the supplied and bounded additional cases.
The next observation is the supplied local development check, bounded to one
recorded command and 45 seconds; actual monetary usage is not available.
Product cost fixtures are illustrative accounting inputs, not measured usage or
productivity of this coding-agent run. Independent acceptance and continuation
belong to the recording operator.
