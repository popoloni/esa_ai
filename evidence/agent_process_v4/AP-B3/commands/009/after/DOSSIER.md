# B3 decision record

## Expect

Sources read before implementation: AGENTS.md; docs/contract.md (approved HISTORY-API/v1 and MIGRATION/v1, 2025-05-21); docs/policy_catalog.json; the actual ledger.py starter; its routing.py dependency; and all supplied tests/test_b3.py tests. The ledger otherwise uses Python standard-library dependencies. The retained router currently implements B1-API/v2 text acceptance with BR-001/v1 business classification. Schema version 2, HISTORY-API/v1, B1 API versions and BR-001 business-policy versions are independent.

Acceptance examples derived before coding:

1. Record amount 4000.0 under request old with BR-001/v1: STANDARD_QUEUE. Activate BR-001/v2; retry old with canonically equivalent 004000.00 and the same beneficiary. Return the entire original record, including original amount spelling and v1 evidence, without another decision or audit event. Reopening the database preserves active v2 and old v1 history.
2. Reuse old with a changed amount, changed beneficiary, or an explicit incompatible policy: IDEMPOTENCY_CONFLICT with no mutation. Ambient activation is excluded from identity. An explicit matching v1 policy is a replay; a new request can use active v2.
3. replay(old) returns stored evidence. recompute(old) calculates with the stored policy snapshot and returns MATCH without a row. reevaluate(old, new, BR-001/v2) records HUMAN_REVIEW with parent old and a distinct identity; using old as the new ID is refused.
4. Ledger decimal fullmatch permits at most 12 ASCII integer digits, optional minus, and at most 2 fractional digits. Leading zeros normalize for identity, including signed zero; stored original fields survive. Plus signs, Unicode digits, final newlines and extra precision are rejected even when another API has broader acceptance. Positive amounts below the chosen threshold use STANDARD_QUEUE; zero/negative amounts are REJECTED; exact thresholds use HUMAN_REVIEW. Every outcome remains routing only with payment_authorized false.
5. Explicit migration of an evidenced synthetic v1 legacy fixture validates application/schema, nonempty synthetic source ID, exact ordered-row digest, historical payload, known policy snapshot and matching outcome. It imports the original JSON, records source evidence, leaves the legacy rows unchanged and makes history immutable. Missing/mismatched provenance, unmapped policy or inconsistent outcome stops the transaction; no current-policy fallback or partial schema conversion is permitted.

Open owner questions and limits: there is no blocking ambiguity for the supplied v1/v2 catalogue. A real or unmapped historical source requires owner-supplied provenance and historical-rule mapping before migration can proceed. The reusable migration API accepts trusted provenance; authentication of the protected synthetic source belongs to the independent owner/operator boundary described in the starter, not an invented production trust mechanism. Future business rules, API changes and catalogue extension are outside this change. No production migration or financial authority is inferred.

## Delegate

Only ledger.py and this dossier may change. Preserve contracts, catalogue, tests, retained router, prior snapshots and metadata. Implement the retry/migration omissions using the existing schema, evidence format and API; keep replay, recomputation and new reevaluation separate. All task reads, edits and checks use the AP-B3 recorder prefix. Development checks use python3 -B to avoid writing bytecode into protected workspace files. Independent protected acceptance and continuation are the operator's responsibility.

## Observe

- AP-B3/001: listed the supplied workspace files; no changes.
- AP-B3/002: read the authorized implementation sources and supplied tests; no changes.
- AP-B3/003: baseline python3 -B -m unittest discover -s tests -v, exit 1. Ten tests ran: seven passed, retry-after-activation failed because the returned record substituted a v2 outcome, and both migration tests errored at the explicit NotImplementedError. These are actual retained failures, not inferred test results.
- AP-B3/004: recorded these acceptance examples and unresolved questions before changing ledger.py.
- AP-B3/005: additional contract-derived development test, exit 1. An existing key with explicit unmapped BR-001/v999 returned UNKNOWN_POLICY instead of the required IDEMPOTENCY_CONFLICT. No workspace changes.
- AP-B3/006: removed retry recomputation, checked existing request identity before resolving a new policy, retained explicit-None selection for new requests, and enabled the starter's transactional provenance-validated migration. Only ledger.py and this dossier changed.
- AP-B3/007: reran the supplied ten tests with the unchanged test file; all ten passed, exit 0. No workspace changes.
- AP-B3/008: eight additional inline development tests passed, exit 0. Covered exact canonical replay after activation; explicit known/unmapped/empty policy conflicts and new-key empty-policy rejection; separate reevaluation/recomputation; ledger/router grammar differences and signed-zero identity; exact noncanonical legacy JSON preservation, source audit evidence and all update/delete guards; byte-identical rollback for missing/mismatched provenance and unmapped/changed historical rules or outcomes; and rollback of DDL when an existing settings table forces a mid-schema failure. Temporary databases were removed by TemporaryDirectory; no development test files or protected files changed.
- AP-B3/009: finalized this dossier and inspected the modified implementation sections. Nine recorded commands used, within the 40-command budget. No operator correction was requested or received during this implementation.


## Decide

- ACCEPT a canonical retry as an exact return of stored evidence; REJECT using policy activation as permission to revise the historical result.
- ACCEPT a read-only recomputation against the recorded snapshot; REJECT recording that verification as a new business decision.
- ACCEPT reevaluation only with an explicit policy and new request identity/parent; ASK for provenance and historical-rule mapping whenever migration evidence is missing or ambiguous, rather than guessing a rule.

Implementation and local development verification are complete. The scoped change is accepted for handoff on the evidence above: 10 supplied tests and 8 additional contract-derived development tests pass. The baseline failures and the additional pre-fix conflict failure remain recorded; they are not erased by later success.

Actual implementation: an existing request returns its validated stored record unchanged; request identity conflicts take precedence over resolving a different requested policy; new requests still reject unknown/empty explicit policies instead of falling back to active policy. The existing explicit migration validation/insertion transaction is now reachable. No router, catalogue, schema format, protected test, prior snapshot or metadata was edited.

Limits: these are local development results, not independent protected acceptance or continuation results. The operator owns those next checks and any protected synthetic-source authorization. The API trusts supplied provenance as documented; neither its digest nor these tests authenticate real-world records. Unmapped history and missing provenance must remain stop conditions. No production migration, fund movement, human participation or unverified model identity is asserted.
