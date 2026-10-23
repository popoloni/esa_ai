# Review records, version 2

This revision repairs four boundaries in the cumulative teaching lab: a current
architecture must agree with the route used downstream; an actual client attempt
must be reportable truthfully; all outstanding upstream reviews must survive a
handoff; and unfamiliar wording must not be called missing reasoning.

The selected routing cases, original decision identities, human approval
boundaries and exact source digests are unchanged. These records describe the
fictional Treasury case. A successful local check does not turn its proposed
architecture into an accepted decision.

## Which files should a new reader use?

The current cumulative references are the twelve pairs in
`reader_side/tools/integration_core.py:INPUT_PAIRS`. Four references now live in
`reader_side/reference_solution/v2/`:

| File | Current schema | Meaning of the version |
|---|---|---|
| `context_packet.json` | `context-packet/v2` | Separates the mandatory review minimum from the complete outstanding upstream review list. |
| `delegation_plan.json` | `delegation-plan/v2` | Carries that list into the still-pending plan and binds its current context source. |
| `delegation_handoff.json` | `delegation-handoff/v2` | Carries the same review list to the next reader. |
| `implementation_report.json` | `implementation-report/v2` | Separates the origin of the teaching case from how this implementation attempt was performed. |

The original files outside `v2/` remain byte-for-byte historical references.
Their original receipts and source digests must not be rewritten. The v2 planning
record retains the business decision identity `PLAN-007/v1` and adds
`record_revision: 2`: this is a fuller record of the same pending proposal, not an
approval. The separately authored fictional lifecycle uses its own new decision.

Run the current cumulative example from the companion root:

```sh
python -B reader_side/tools/integration_gate.py --reference
```

Its successful status is `PASS_REVIEW_GATE_ONLY`, with `canonical_route: DIRECT`.
Its authority block still records the pending human architecture decision and
blocked implementation task in the original planning exercise.

## 1. Direct is the supplied cumulative route

Chapter 5 still permits both `direct` and `ports` as valid design explorations.
The supplied context, planning and implementation continuation uses **direct**.
The new `CP05_CP07_canonical_route` layer compares the current selection with that
downstream route and the decision-bearing fields of the pinned planning source.

Selecting ports locally can therefore pass the Chapter 5 design review and still
receive `UNSUPPORTED_CUMULATIVE_ROUTE:ports` from the cumulative gate. This is a
route diagnostic, not a claim that ports is a bad design. Preserve the exploration
and deliberately choose the supplied direct continuation, or create a separately
versioned ports continuation with matching context, plan and receipts. The gate
does not overwrite a selected design, copy a reference into a learner file or
silently accept inconsistent branches.

## 2. Record the actual kind of implementation attempt

In a v2 implementation report the following three fields answer different
questions:

| Field | Allowed value | Question answered |
|---|---|---|
| `fixture_origin` | `SYNTHETIC_TEACHING_CASE` | Where did the business scenario and selected cases originate? |
| `execution_mode` | `OFFLINE_DETERMINISTIC` or `ACTUAL_AGENT_CLIENT` | How was this implementation attempt performed? |
| `observed_run_ref` | `null`, or a `{path, sha256}` reference | Which retained observation supports a claim about an actual client attempt? |

An offline reference has `observed_run_ref: null`. A real learner attempt may use
`ACTUAL_AGENT_CLIENT` while the business case remains synthetic. A model call does
not turn a fictional Treasury scenario into observed user research. Conversely,
synthetic case inputs are not a reason to deny that a learner actually used a
client.

For an actual attempt, retain an observation file with these fields:

| Field | Contract |
|---|---|
| `schema` | `agent-client-observation/v1` |
| `record_kind` | `ACTUAL_EXECUTION_RECORD` |
| `execution_mode` | `ACTUAL_AGENT_CLIENT` |
| `change_id` | `IMPL-008/v1`, matching the implementation report |
| `claim_scope` | `CLIENT_ATTEMPT_ONLY_NOT_ACCEPTANCE` |
| `run_id` | Nonempty identifier for this attempt |
| `client` | Nonempty `name`, `version` and `model` strings |
| `environment` | Description of the actual execution environment |
| `started_at`, `ended_at` | ISO timestamps with time zones; end must not precede start |
| `outcome` | `COMPLETED`, `FAILED` or `INTERRUPTED` |
| `candidate_sha256` | SHA-256 of the exact candidate reviewed by the gate |
| `transcript_ref` | `{path, sha256}` of the retained attempt transcript |

Both references use paths relative to the companion root. Store observations and
transcripts under a dedicated evidence directory, outside `repo/`, so recording
them does not expand the CP08 code edit scope. Absolute paths, traversal and
symlinked evidence are rejected. A changed observation, transcript or candidate
invalidates its binding. The cumulative receipt includes both evidence files so
that a previously passing receipt also becomes stale when either changes.

Populate these fields only from a run that occurred. The gate checks schema,
internal consistency and byte binding. It cannot establish external authenticity
from a user-written JSON record, and it does not infer model compliance or human
acceptance. Keep the original transcript, review what it supports and state its
limitations. A failed or interrupted client attempt is still an actual attempt;
its outcome must be recorded honestly.

The CP08 domain fields still describe an explanation-only change, the proposed
architecture, unresolved questions and a candidate ready for human review. Actual
client mode grants no payment, architecture-acceptance or release authority.

### Legacy reports

A report with no schema, or `implementation-report/v1`, remains valid only with
`live_agent_run: false`. It is labeled `LEGACY_V1_OFFLINE_COMPATIBILITY` in the
cumulative output. Do not change a historical report to describe a later attempt.
Create a new v2 attempt report and retain the old evidence. V2 rejects the old
`live_agent_run` flag because keeping both representations would be ambiguous.

## 3. Preserve every pending upstream decision

The historical minimum is `ADR-005` plus `OPERATOR_COPY`. V2 records this in
`mandatory_human_reviews`, and records the complete known outstanding list in
`pending_reviews`:

| Review | Subject | Accountable role | Current state |
|---|---|---|---|
| `SPEC-004` | `SPEC-004/v1` | Product Owner in the synthetic scenario | `PENDING_HUMAN` |
| `ADR-005` | `ADR-005/v1` | Technical Lead in the synthetic scenario | `PENDING_HUMAN` |
| `OPERATOR_COPY` | `SPEC-004/v1#operator-copy` | Product Owner in the synthetic scenario | `PENDING_HUMAN` |

Each record has `review_id`, `subject_ref`, `owner_role`, `status` and
`decision_ref`. All current records have `decision_ref: null`. A claimed approval
without a separate authorized decision is rejected rather than silently promoted.

The same records appear in the v2 plan and its handoff. `T07-03` names both
requirements and architecture decisions; `T07-06` carries operator-copy review
alongside the later release decision. The first two read-only investigations
remain ready, and the writer remains blocked. Recording another pending review
cannot authorize work.

A legacy context may truthfully add `SPEC-004` to `human_review_required`; the
local context gate now accepts that known extra review. The cumulative gate also
requires it to reach planning. An unknown review is `HUMAN_REVIEW_UNKNOWN`, a
missing required decision is `HUMAN_REVIEW_MISSING:<id>`, and an invented approval
is `PENDING_REVIEW_UNSUPPORTED_APPROVAL:<id>`. These are different problems and
receive different diagnostics.

## 4. Understand semantic-review findings

Identifiers, versions, digests, policy outcomes, source IDs and authority states
remain exact checks. A prose explanation is different. Prefixes and keywords can
recognize the book's example, but they cannot prove whether an unfamiliar
sentence carries the same meaning.

The discovery, specification, architecture, knowledge and planning checks now use
`HUMAN_SEMANTIC_REVIEW` when nonempty prose falls outside the small lexical rubric.
For example, a sentence saying that only the requirements owner should assess an
explanation-only alpha is no longer labeled as *missing requirements review*
solely because it does not begin with the reference sentence. Empty required text
is still `TEXT_MISSING`; wrong source IDs, case outcomes and authority states
remain hard failures.

When semantic review is the only outstanding matter, the cumulative result and
affected layer explicitly report `HUMAN_SEMANTIC_REVIEW`. The command does not
return a passing exit code. A reader should compare the wording with the stated
authority boundary and record a human judgment; changing words merely to satisfy
the rubric is not evidence that the reasoning improved. This revision does not
add an automatic human-approval override or weaken the protected oracle.

## Verification and preservation

`reader_side/tests/test_revision_contracts_v2.py` reproduces the ports/direct
mismatch, actual-attempt provenance constraints, extra pending review, and
equivalent handoff. It includes positive current/legacy paths and negative checks
for stale evidence, path escape, invented approval and lost review propagation.
Observation records created by these unit tests are explicit synthetic test
doubles; no actual model execution is claimed by the test run.

The existing suite retains exact candidate, stale-receipt and Chapter 10
source-authority checks. Original changed checker/test bytes and their old
manifest are preserved in the book package's `history/d3/core_revision_baseline/`.
