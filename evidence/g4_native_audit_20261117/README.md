# G4: current regression checks and a separate correction

The retained Claude run passed its original eleven protected G4 methods. On
17 November 2026, an independent audit found a contract case that those methods
did not cover: two recognized **current** reservation representations in one
database. OPS-G4/v3 requires a refusal. The native implementation instead preferred
`reservations_v2` and ignored the recognized current `reservations` table.

An older historical table with a different column signature may coexist with the
current table. The defect concerns two complete, recognized current signatures;
it does not introduce a new schema mapping or expand operational authority.

## Observations

- [The original eleven-method receipt](../native_claude_20261116/work/evidence/g4-first.json)
  remains unchanged.
- [The same operation source against the current thirteen-method suite](receipts/original_native.json)
  fails the two new ambiguity checks.
- [A separate minimal correction](G4_AUDIT_CORRECTION.diff), authored by the present
  AI audit operator, [passes thirteen methods](receipts/audit_correction.json).
- [The reference implementation also passes thirteen methods](receipts/reference_operations.json).
- [Independent SQL controls](independent_schema_controls.json) confirm that each
  of the three individual representations works and expose both competing pairs.

The correction is not a fresh Claude model run. It does not change the retained
Claude candidate, its events, its decisions, or its original passing receipt.
The audit candidates contain refreshed protected tests and fixture metadata so
the old operation source can be assessed by the current suite. The receipt paths
record the original audit working directories; the copied files and source hashes
are indexed in [AUDIT.json](AUDIT.json).

## Replay the current controls

The `candidates/` and `receipts/` directories preserve the original audit records,
including their earlier release identity. The strict current release guard
correctly refuses those older entries. The separate `replay_candidates/` copies
change only the top-level `READER_ENTRY.json` **release** field to edition 5.2.
Every implementation and protected input byte remains identical to its audit
source. No compatibility guard was weakened and no native history was edited.

[The metadata-only rebinding record](REPLAY_REBIND_20261117.json) identifies the
old and current entry hashes and the new checks. The current replay of the
[original source](replay_receipts/original_native.json) fails exactly the two
new methods; the [correction](replay_receipts/audit_correction.json) and
[reference](replay_receipts/reference_operations.json) both pass thirteen.

From the companion root, choose fresh receipt paths outside these retained
candidate inputs:

```sh
python3 -B companion/start.py check G4 --candidate evidence/g4_native_audit_20261117/replay_candidates/original_native --output work/g4-audit-original.json
python3 -B companion/start.py check G4 --candidate evidence/g4_native_audit_20261117/replay_candidates/audit_correction --output work/g4-audit-correction.json
```

The first command should fail two of thirteen methods; the second should pass all
thirteen. These are deterministic product checks. They do not launch a model,
measure a human learner, or provide production authorization.
