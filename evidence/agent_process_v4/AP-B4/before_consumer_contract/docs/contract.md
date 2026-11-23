# B4: wrong-ledger diagnosis and recovery planning

Owner: fictional service operations lead. Approved teaching contract (fictional case date) OPS-B4/v1,
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
