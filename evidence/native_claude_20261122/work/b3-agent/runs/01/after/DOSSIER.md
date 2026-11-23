# B3 decision record

## Expect

Contract: HISTORY-API/v1 + MIGRATION/v1 (docs/contract.md, docs/policy_catalog.json). Read AGENTS.md, contract and catalogue; I found no conflict between them and no missing consequential rule for this increment.

Outcome: a request retried under the same ID and canonical payload returns the stored decision even after the active policy changes; legacy migration is explicit and transactional.

Acceptance example: decide("original", 4000.00) under BR-001/v1 -> STANDARD_QUEUE; activate(BR-001/v2); the same decide returns status REPLAYED with a record identical to the original (still STANDARD_QUEUE, policy BR-001/v1), and the decisions/audit_events row counts do not change. A fresh ID with the same payload now gives HUMAN_REVIEW.

Open owner question: none blocking. The task mentions "three proposals", but no proposals were supplied in the workspace, so I cannot rule on them (see Decide).

## Delegate

Edits only in ledger.py:
1. `PolicyStore._decide`: on an existing key, the replay path re-ran `outcome()` under the currently active policy and overwrote `record["decision"]`. This broke exact replay after activation. I removed that recomputation; the stored record is returned unchanged.
2. `migrate_legacy`: the body began with `raise NotImplementedError(...)`, which made the rest unreachable. I removed that line. The retained body already checks the schema, provenance (schema, origin, source_id, rows digest), historical policy and outcome, and runs in a single transaction. It leaves legacy_decisions in place and adds update/delete triggers on it.

Not touched: routing.py, tests, docs, prior/, READER_ENTRY.json, the public interface, the catalogue and the amount grammar.

## Observe

- `python3 -m unittest tests.test_b3` before edits: 10 tests, 1 failure (retry after policy change returned the v2 outcome) and 2 errors (NotImplementedError in both migration tests).
- Same command after edits: 10 tests, OK.
- Ad-hoc probe (a script in the session scratchpad, a temporary database): "+1.00", "1.00\n", a fullwidth digit, 13 integer digits and 3 fractional digits are all rejected with INVALID_AMOUNT_FORMAT. "007.5" is accepted. "-0" is accepted and routed to REJECTED. An explicit v2 under an old v1 ID raises IDEMPOTENCY_CONFLICT. Retrying with explicit v1 is REPLAYED. A new ID under active v2 gives HUMAN_REVIEW. Row counts matched expectations (4 decisions, 5 audit events).

## Decide

- Fix 1 (replay returns the stored record): ACCEPT. It is required by the contract and by the failing test.
- Fix 2 (enable the migration): ACCEPT. It was a placeholder guard over an already-written implementation.
- Handoff scope: ledger.py and this dossier only. I ran only the local checks above. The operator will run protected acceptance and continuation.
- The "three proposals" were not supplied: no ruling is made on them. Please provide them if they are expected.

Limits and remaining uncertainty:
- Only the one supplied legacy fixture shape was exercised. Migration failure paths (ambiguous policy, outcome mismatch, wrong schema) are by reading, not by test.
- Concurrency and a crash mid-migration were not tested.
- The contract notes that B1-API/v2 allows "+" and up to 32 characters, which the ledger boundary rejects by design. Not changed.
- Human acceptance is not given. These are local checks and grant no production or financial authority.
