# A rollout and migration decision sheet

Status: ORIGINAL TABLETOP DESIGN, NOT A DEPLOYMENT RECEIPT.

## Filled transfer case: change a response representation

A proposed API replaces the top-level `policy_version` with `policy.version`. Its routing result and payment prohibition must remain the same. The two local readers in `contract_drill.py` illustrate the compatibility obligation; no real HTTP API or deployed client inventory has been collected.

1. **Inventory:** name the old/new readers, supported versions and unknown consumers. Unknown consumers prevent a claim that all consumers migrated.
2. **Expand:** produce both version fields with the same value while preparing the new reader. Run the selected consumer probes. An extra field is safe only for readers whose actual decoding permits it.
3. **Migrate use:** update each consumer and retain evidence that its deployed version uses the supported representation. The local probe demonstrates code behavior, not fleet adoption.
4. **Contract:** remove the old field only under an explicit deprecation decision after its consumers and rollback dependence are resolved. Retain the earlier contract and evidence.
5. **Reverse or stop:** define which producer and reader versions can coexist. Returning the producer to a version without the nested field can break a migrated reader. Keeping a previous binary is not a complete recovery plan.

## Persisted-state variation

Suppose the same representation change affects stored policy history. Prepare readers before enabling a new writer format, then verify the nominated downgrade target can read records written during activation. Do not remove old-format readers while retained records still need them. A migration must preserve the original policy identity; a missing historical version is not permission to insert today's version. Unknown provenance blocks conversion under CP11's contract.

Before any real migration, the data owner must choose backup/restore or forward-repair behavior, validate restoration on representative copies, record lock/throughput limits, and define what stops the backfill. This worksheet does not establish that an online SQLite migration, a fleet rollback, or a distributed transaction has been tested.

## Traffic exposure and state side effects

A release plan needs a population, a time window, selected signals, minimum evidence, stop criteria, rollback/forward-repair target and an operator. A default-off feature switch controls only the effects it actually gates. Initialization, background work or schema changes can occur even when the visible feature is off. A shadow request must not emit payments, messages or other repeated effects; an isolated output sink is a design requirement to verify, not a setting assumed from the word shadow.

For the Treasury transfer, watch the emitted policy identity, correct new/retry semantics and selected state as well as success/latency. Healthy HTTP responses would not expose CP12's wrong-history result. Compare the exposed group with a meaningful control, consider shared dependencies, and retain the absolute service objective. No arbitrary traffic percentage guarantees safety.

## Blank decision record

- Change and exact candidate:
- Consumers, data formats and unknowns:
- Authorized operation owner:
- Expansion/preparation evidence:
- Activation conditions and minimum observations:
- Selected exposure, observation window and rationale:
- Signals and data source, with missing-telemetry action:
- Stop criterion and who acts:
- Recovery target and compatible retained state:
- Effects that cannot be reversed by selecting code:
- Reconciliation/forward-repair owner:
- Contraction/deprecation condition:
- Evidence still missing and next review:

Primary grounding: AWS Builders' Library on mixed-version compatibility and prepare/activate rollback boundaries; Google SRE on partial exposure, evaluation and monitoring attribution. All Treasury details above are author-created design work. Neither source validates this unexecuted plan.
