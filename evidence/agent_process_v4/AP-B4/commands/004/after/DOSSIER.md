# B4 decision record

## Expect

Authorized source: AGENTS.md, docs/contract.md (OPS-B4/v1, fictional 2025-05-22), docs/policy_catalog.json, incident.py starter, retained ledger.py/routing.py, operations.py and tests/test_b4.py. The scope is synthetic diagnosis and recovery planning. It supplies no production, payment, or reconciliation authority.

Concrete acceptance examples, recorded before incident.py edits:

1. Create expected.sqlite and wrong.sqlite with the same retained PolicyStore source and the same old request (EUR 4000.00). Add owner anchor `anchor` (EUR 12.00) and activate BR-001/v2 only in expected.sqlite. Selecting wrong.sqlite must report WRONG_LEDGER with STATE_PATH_MISMATCH, ACTIVE_POLICY_MISMATCH and ANCHOR_MISSING, while both byte sequences remain unchanged. Both copies of `old` may have the same deterministic decision ID; that does not establish common replay lineage.
2. Select expected.sqlite against itself with expected policy BR-001/v2 and the supplied anchor. Report EXPECTED_LEDGER_SELECTED, no issues, observed v2, historical decisions and audit count, and the actual resolved selected path and file digest.
3. Inspect a nonexistent path: raise FileNotFoundError without creating it. Refuse an unsupported schema, unrelated application ID, or invalid historical integrity without initializing or migrating anything.
4. If the anchor key exists in both ledgers but the stored evidence differs, report ANCHOR_MISMATCH. If the proposed expected state lacks the supplied anchor or expected policy, stop with explicit reference-evidence failure; do not invent history or recommend that state as a verified restoration target.
5. A recovery plan preserves both paths/digests, proposes restoring the expected binding, and names historical replay, a fresh-key current-policy probe on a disposable copy, and restart/state checks. It performs no restore or merge, has production_authorized=false, and leaves reconciliation PENDING_OWNER_DECISION.
6. Two attempts costing EUR 1.2/8 minutes and EUR 0.8/12 minutes with one accepted outcome total EUR 2.0 and 20 minutes per accepted outcome. The failed attempt remains included. Zero accepted outcomes must retain totals without division by zero.

Open owner choices: disposition of any wrong-ledger records; conflict analysis and supporting evidence; production restoration authorization; the specific operational restart mechanism. No owner reconciliation or production decision is supplied, so none will be inferred. Diagnosis accepts only stable evidence snapshots: an active WAL/journal cannot be ignored while claiming that the main-file digest describes the observed state. Such an input will be refused for an owner-provided stable snapshot, not changed or checkpointed.

## Delegate

Edit only incident.py and this dossier. Reuse operations.cost_summary and retain ledger/router behavior unchanged. Inspect through a read-only SQLite URI, validate HISTORY schema/application identity and stored evidence, bind observations to resolved paths and byte digests, and check preservation across the observation. Return a proposal with explicit owner gates, not an operational recovery executor. Source identity in the handoff will use hashes of the actual retained ledger/router source, without inventing a release label.

A reasoning-only helper was attempted but unavailable because the agent-thread limit had been reached; no helper read or edited files. All filesystem reads, edits and checks use the required AP-B4 recorder.

## Observe

- AP-B4/001: read AGENTS.md and inventory of the supplied workspace; exit 0; no changes.
- AP-B4/002: read every supplied docs contract/catalog, incident starter, retained ledger/router, accounting implementation, supplied tests and initial dossier; exit 0; no changes.
- AP-B4/003: baseline `python3 -B -m unittest discover -s tests -v`; exit 1. Six tests ran: five errors from NotImplementedError in incident.py; the existing cost-summary test passed. The recorded failure is retained as part of the actual attempt history.
- AP-B4/004: record expectations, acceptance cases, unresolved owner choices and implementation bounds before editing incident.py.

Checks are development feedback. Independent protected acceptance and continuation remain with the AI recording operator; the operator is not a human study participant. Measured monetary cost and elapsed effort are not supplied, so the accounting fixture is illustrative and no actual cost figure is invented.

## Decide

- ACCEPT: implement read-only diagnosis and an evidence-bound proposal to restore the verified expected binding, within the teaching scope and subject to separate operational authorization.
- REJECT: automatic row merging, treating a deterministic ID as proof of shared replay lineage, changing policy merely to conceal the wrong binding, or declaring production recovery/reconciliation complete.
- ASK: the owner must decide the treatment of wrong-state records using conflict analysis and separate evidence. This does not block implementing the explicitly authorized diagnosis/planning API.

Analytical handoff will identify selected state, actual source fingerprints, observed policy, preserved evidence, proposed restoration, unresolved reconciliation and the next authorized check. No production incident is claimed.
