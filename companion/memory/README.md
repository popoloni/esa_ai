# Keep memory useful when a contract changes

This optional B1 lab makes an external memory lifecycle executable: propose a
claim, bind its source and observation, obtain a separately declared promotion,
retrieve it within a current scope, and revoke it when contrary evidence arrives.
It adds no mission and changes no existing contract. Python 3.10 or later and the
standard library are sufficient; no model account, network call or vector store
is used.

Memory here means retained records supplied to a later task. Updating them does
not change model weights. Passing this lab's checks does not establish that a
person learned the decision, retained it later or transferred it to a new task.

## Run the whole example

From the package root, alongside `companion/` and `evidence/`:

```bash
python3 companion/memory/demo.py --output work/memory-b1
```

Choose a fresh directory for another attempt. The command executes the supplied
B1 reference functions, creates a local authority fixture, exercises the ledger
through its real CLI, and saves every invocation, result and ledger event.
`work/memory-b1/RESULTS.json` gives the observed checks and their limits.

The [retained demonstration receipt](../../evidence/memory_lab_20261116/recorded_01/RESULTS.json)
provides an inspectable execution of the same lab. The separate
[actual development case](../../evidence/handbook_memory_20261116/reject_correct_01/CASE_GUIDE.md)
shows an independently found ledger defect, an AI operator's REJECT, a bounded
repair and the recheck. It is distinct from the deliberately wrong memory card
used below.

All producer and approver identities in this demonstration are labelled
`automated_control`. The wrong approved card is deliberately planted to test
revocation. It is not an agent error or a human approval. The ledger's query time
is set two hours after fixture creation to exercise an expiry; this does not
claim that the demonstration waited for two hours.

## One business rule, two API scopes

[BR-001/v1](../context/BR-001.md) classifies a finite positive amount below EUR
5,000 into `STANDARD_QUEUE`, and equality or a larger amount into `HUMAN_REVIEW`.
The classification does not authorize a payment.

[B1-API/v1](../contracts/B1_API.md) accepts Decimal-supported textual forms such
as `1e3`. The separately created [B1-API/v2](../contracts/B1_API_V2.md) candidate
requires the owner's explicit ASCII monetary-text grammar. It rejects exponent
notation and permits a leading plus sign within the length and numeric rules.
Both versions still return `policy_version=BR-001/v1`; the unchanged business
identifier alone cannot select the correct API memory.

The query therefore names four dimensions independently:

| Scope | Value used in this lab | What a mismatch means |
|:--|:--|:--|
| Task | `B1-grammar-check` | The card was prepared for a different decision. |
| Component | `treasury.routing.assess` | Another component may have different obligations. |
| Contract/API | `B1-API/v1` or `B1-API/v2` | The lexical rules are not interchangeable. |
| Schema/shape | `RoutingDecision(route,reason,policy_version)` | A changed output shape needs a new review. |

The schema string describes the fields in the supplied API; it does not invent
a new product contract. The ledger record itself has the separate technical
format identifier `agent-memory-record/v1`.

## Inspect the decisions that changed retrieval

| Observation | What the demonstration establishes | Retained receipt |
|:--|:--|:--|
| A source-backed proposal exists but has no promotion | Proposal storage alone does not make it retrievable. | `receipts/pending_not_retrieved.json` |
| A caller claims an owner identity without a matching local grant | Promotion is refused; the proposal remains. | `receipts/promote_B1-V1-EXPONENT_wrong_actor.json` |
| An approval names the wrong record digest | Approval cannot transfer to different bytes. | `receipts/promote_B1-V1-EXPONENT_wrong_hash.json` |
| An approved v1 exponent card meets its v1 query | The applicable card is returned with provenance. | `receipts/v1_retrieval.json` |
| The query changes to v2 | The v1 card is excluded by scope; its history stays approved. | `receipts/v1_excluded_from_v2.json` |
| A card has expired at the declared query time | It is excluded, without rewriting its historical status. | `receipts/expired_excluded.json` |
| A current v2 card fits the scope and validity interval | It is retrieved. | `receipts/v2_retrieval.json` |
| The response budget is too small for a complete card | The card is omitted, with a count; its provenance is not truncated. | `receipts/small_output_budget.json` |
| A deliberately wrong v2 card says all leading-plus inputs are rejected | The actual reference probe of `+4999.99` returns `STANDARD_QUEUE`, contradicting that claim. | `observations/plus_counterevidence.json` |
| A revocation cites the wrong counterevidence digest | Invalidation is refused until the reference is bound correctly. | `receipts/wrong_counterevidence_refused.json` |
| The declared owner control revokes the false card | The card stays in history as `revoked` and is absent from retrieval. | `receipts/after_contradiction.json` |
| A corrected version is proposed | It needs a new promotion; it does not inherit the revoked card's approval. | `receipts/correction_pending.json` |
| A bound source copy changes | Its card is excluded despite its earlier approval. | `receipts/changed_source_excluded.json` |

The reference probes preserve their actual code hashes and returned values.
They are observations about supplied reference code, not acceptance results for
your learner candidate. The v1 exponent case is an applicability boundary; the
false v2 plus-sign claim is a contradiction. Treating both as “stale memory”
would hide the different next actions.

## What a memory card retains

| Field group | Contents |
|:--|:--|
| Identity and type | Record ID, record version, `fact`/`procedure`/`decision`, claim, claim-content digest and complete-record digest. |
| Scope | Exact task, component, contract/API and output shape. Wildcard scope is refused. |
| Producer | Declared producer ID and kind: human, model agent or automated control. |
| Authority and observations | Separate source and evidence references, each with path, SHA-256 and locator. |
| Dates | Actual proposal event time, declared last-check time, valid-from time and expiry. |
| Promotion | Declared actor, matching local grant, authority source, exact record digest, and the decision file's path and digest. |
| Revisit conditions | Contract, component or shape changes; changed source/evidence/approval identity; contradiction; expiry. |
| State and correction | `proposed`, `approved` or `revoked`, retained invalidation evidence, and an explicit predecessor for a corrected version. |

A file digest proves that retrieved bytes match the bytes previously referenced.
It does not prove that the source is authoritative, that a claim follows from
it, or that the observation discriminates the claim. The deliberately wrong
approved control card makes that limitation visible. A real reviewer must read
the authority, claim and observation together before promotion.

## Reuse the CLI without rerunning the demonstration

Inspect a retained card and its computed state:

```bash
python3 companion/memory/ledger.py \
  --workspace . --ledger work/memory-b1/events.jsonl \
  inspect --record-id B1-V2-PLUS-WRONG
```

The current record is `revoked`; the proposal, approval and invalidation remain
in `events.jsonl`. `B1-V1-EXPONENT` is still historically `approved`.

For an identical dated query, copy `retrieval_as_of` from `RESULTS.json` into
`MEMORY_AS_OF`. In a POSIX shell:

```bash
MEMORY_AS_OF=$(python3 -c "import json; print(json.load(open('work/memory-b1/RESULTS.json'))['retrieval_as_of'])")
python3 companion/memory/ledger.py \
  --workspace . --ledger work/memory-b1/events.jsonl \
  retrieve --task B1-grammar-check \
  --component treasury.routing.assess --contract B1-API/v2 \
  --schema 'RoutingDecision(route,reason,policy_version)' \
  --at "$MEMORY_AS_OF" --limit 2 --max-bytes 12000
```

Retrieval first checks state, exact scope, dates, source/evidence/approval
identities and the declared grant. Only then does it order applicable cards by
last-check date, version and ID. Recency cannot authorize a different scope.
The limit bounds complete records and the UTF-8 byte budget bounds the entire
JSON response. An empty result means that no complete applicable card was
returned; inspect the exclusion and budget counts before concluding that the
ledger contains no history.

For your own experiment, create a new ledger with `init --policy FILE`, then use
`propose --record FILE`. Use the generated proposal files as schema examples.
Promotion requires a separate decision file binding the record digest and all
reviewed source/evidence references. `promote` and `invalidate` also require an
explicit actor ID and kind. See `ledger.py --help` and each subcommand's `--help`
for the complete interface. Do not reuse the demonstration's declared owner
identity as evidence of actual approval.

## Keep the boundaries visible

The application appends JSONL events and refuses an existing record ID. A
correction creates a new ID and next version linked to a revoked predecessor.
An exclusive writer lock prevents cooperating application writers from
interleaving. Each event binds the previous event digest, and the demonstration
detects an altered event in a separate copy. These controls are not append-only
filesystem enforcement: the file owner can rewrite the ledger and recompute
the chain. A production service needs its own authenticated identities,
authorization, retention controls and appropriate audit storage.

The local authority file is itself hash-bound and grants exact scopes. Actor
names on the CLI remain declarations. An agent running as the same OS user can
claim a name or edit files; the ledger does not turn a text label into verified
owner authority. The same declared producer cannot promote its own record even
if its name has a grant; the program cannot detect a forged alternative identity.
Keep actual promotion outside the proposing agent's permitted
actions and enforce that separation in the real runtime.

A broken or partially written event chain stops processing. Preserve the
original bytes and inspect the last verified event before an authorized recovery
to a separate file. The lab does not silently drop a damaged tail, overwrite
history or claim to provide transactional recovery after a filesystem failure.

The lab refuses a proposal with no observed evidence, a structured
`instruction_override` type, and a proposal explicitly labelled `secret`.
The secret fixture contains only a synthetic marker. Refusal events keep the
reason and input-file digest, not the submitted claim. These closed-schema
checks are not a general secret scanner or prompt-injection defense. A malicious
instruction disguised as a fact still requires content review. Retrieved text
must not override the current task, source authority or tool permissions.

## Use the memory in an agent task

[TASK.md](TASK.md) supplies bounded prompts for retrieval, citation and a
proposed update. They are instructions for a future run, not a claim that an
agent has executed this lab. The proposer must stop for the actual authorized
reviewer; it cannot approve its own memory by borrowing the demo actor name.

To evaluate learning, ask a person to predict retrieval and the next action
before running the controls, retain the assisted attempt, then reduce support.
Use a later retention check and an unexposed structural transfer task separately.
Ledger checks measure the workflow's behavior; those human observations measure
learning. The book's Chapter 12 develops that distinction.

The [three-volume reading guide](../series/READING_THE_SERIES.md) points to the
deeper memory and human-learning treatments in *Non-Deterministic Software
Engineering*, second edition.
