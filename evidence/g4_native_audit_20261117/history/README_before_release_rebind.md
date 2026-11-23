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

From the companion root, choose fresh receipt paths outside these retained
candidate inputs:

```sh
python3 -B companion/start.py check G4 --candidate evidence/g4_native_audit_20261117/candidates/original_native --output work/g4-audit-original.json
python3 -B companion/start.py check G4 --candidate evidence/g4_native_audit_20261117/candidates/audit_correction --output work/g4-audit-correction.json
```

The first command should fail two of thirteen methods; the second should pass all
thirteen. These are deterministic product checks. They do not launch a model,
measure a human learner, or provide production authorization.
