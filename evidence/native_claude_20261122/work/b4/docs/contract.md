# B4: wrong-ledger diagnosis and recovery planning

Owner: fictional service operations lead. Approved teaching contract (fictional case date) OPS-B4/v2,
2025-05-22. The fault fixture uses the same ledger code with a different selected
SQLite state path. The expected ledger has active BR-001/v2 and an owner-supplied
historical anchor; a fresh wrong ledger defaults to v1. A routing difference can
therefore arise without a source-code regression.

inspect_ledger(path) reads an existing HISTORY schema 2 database in read-only mode,
verifying its application ID. Return selected path, digest, active policy,
decisions and audit count. A missing path must not be created. diagnose(selected,
expected,expected_policy=...,anchor_key=...) reports path, policy and anchor
mismatches while leaving both ledgers unchanged. A deterministic decision ID can
occur in both ledgers and is insufficient by itself to establish replay lineage.

recovery_plan(diagnosis) proposes restoring the expected state binding and
preserving both ledgers. It names historical replay, a new-current-policy probe
on a disposable copy and restart/state checks. It does not merge rows, authorize
production recovery or close reconciliation. Distinguish restoring service from
deciding what to do with records created while the wrong state was selected.
The latter requires the owner, conflict analysis and separate evidence.

Reuse accepted-outcome accounting from G4, including failed diagnosis/recovery
attempts. The analytical handoff names selected state, source version, observed
policy, preserved evidence, restoration decision, unresolved reconciliation,
and the next authorized check. No production incident is claimed.

## Explicit recovery-plan consumer boundary (v2)

The local continuation consumes `recovery_plan` as a structured proposal. It must
include `restore_configuration_to` with the resolved expected ledger path,
`automatic_merge` false and `production_authorized` false. Other explanatory
fields and compatibility aliases are permitted. This field identifies a proposed
binding; returning it does not perform or authorize restoration. The operator
still owns the separate local fixture change and subsequent checks.

This consumer-field contract was made explicit on 16 November 2026 after an actual
correctly scoped v1 proposal used another descriptive field name. The earlier
six-method v1 result remains valid under its original stated interface. The
extension is an authored teaching decision, not a retroactive agent failure or a
live operations owner's approval.
