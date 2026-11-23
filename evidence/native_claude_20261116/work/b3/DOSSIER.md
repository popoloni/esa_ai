# B3 decision record

## Expect

Contract: HISTORY-API/v1 + MIGRATION/v1 (docs/contract.md), policy catalogue in
docs/policy_catalog.json. No conflict found between the documents and no missing
policy or mapping, so no owner question is open for this increment.

Outcome: a decision recorded under BR-001/v1 is returned unchanged on retry after
activating BR-001/v2, and an explicit, provenance-checked legacy migration works.

Acceptance example: decide("original", {4000.00, supplier_41}) under v1 gives
STANDARD_QUEUE. After activate("BR-001/v2"), the same request ID and payload
returns status REPLAYED with a record equal to the original, still STANDARD_QUEUE
under BR-001/v1, and adds no decision or audit row. Re-evaluating under v2 with a
new ID gives HUMAN_REVIEW and records the parent.

## Delegate

Two changes in ledger.py. The public interface, routing.py, docs, tests, prior/
and READER_ENTRY.json are untouched.

1. `_decide` replay: on an idempotent retry it overwrote `record["decision"]`
   with `outcome(payload, <currently active policy>)`. After activate(v2) the
   retry therefore showed HUMAN_REVIEW instead of the stored v1 decision. I removed
   that recomputation, so the stored record is returned as is.
2. `migrate_legacy`: it began with an unconditional
   `raise NotImplementedError`, which made the rest of the body unreachable. I
   removed that line. I added no new migration logic. The existing body checks the
   provenance schema, origin, source_id and rows digest. It rejects ambiguous
   policy and mismatched outcomes, and it is transactional.

## Observe

- `python3 -B -m unittest discover -s tests -v` before the changes: 10 tests,
  1 failure (retry returned a recomputed v2 decision) and 2 errors (the migration
  tests hit NotImplementedError). A first attempt with `python3 -I` failed with
  an import error because `-I` removes the working directory from the path. That
  was a command problem, not a code defect.
- The same command after the changes: Ran 10 tests, OK.
- Extra probe (scratchpad script, not part of the repo): "4000.00\n", "+4000" and a
  Unicode digit are rejected with INVALID_AMOUNT_FORMAT. "0004000.5" and "-0" are
  accepted with the original text stored. An explicit v2 request under an old v1 ID
  raises IDEMPOTENCY_CONFLICT. The REPLAYED retry added no audit row.
- Commands run: 8 tool calls beyond reading, within the 40-command allowance.

## Decide

- Fix the replay decision: ACCEPT. The check passes and the contract requires it.
- Remove the NotImplementedError guard so the existing migration runs: ACCEPT,
  limited to the synthetic fixture. This is not production migration authority.
- Any new policy, mapping or default for legacy rows that lack provenance: ASK.
  I added none and the contract defines none.

Limits and uncertainty:
- Only the 10 supplied checks and one ad-hoc probe were run. Protected acceptance
  has not been run, and human acceptance is PENDING.
- The migration adds immutability triggers on `legacy_decisions`. The table rows
  are unchanged, but the schema gains triggers. The contract's "retains the legacy
  table unchanged" could be read to exclude that. I kept the retained behavior
  and flag it for the owner.
- The migration is only exercised with one legacy row. Multi-row, failure
  rollback and concurrent-access cases were not tested.
- Only v1 amounts accepted by the ledger grammar reach routing.assess. The ledger
  rejects values that the B1-API/v2 router allows, such as a plus sign. The
  contract describes this as intended.
- Handoff scope: ledger.py and DOSSIER.md only.
