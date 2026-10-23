# Companion site of Engineering Software with Agentic AI

This is the cumulative laboratory for *Engineering Software with Agentic AI*,
edition `2026.10.22-d9`. Run commands from the directory containing
`reader_start.py`, called `companion/` in the complete author package. Keep the
extracted release unchanged and create separate study copies.

The observed baseline is Linux, Python 3.12.14 and Git 2.51.1. The core declares
Python 3.10 as its language floor and needs Git with `merge-tree --write-tree`
support. The observations do not establish other operating systems or Python
versions as supported. The core uses synthetic records, the standard library
and local processes without a model account. Optional `practice/` integrations
state their own dependencies. `RUNTIME_MATRIX.json` separates current runs,
historical receipts and pending external observations.

Start with `navigation/FIRST_WEEK.md` for the cumulative Treasury route, or
`navigation/EXPERIENCED_PREVIEW.md` for the self-contained CSV task. Both ask you
to make a bounded change, check it independently and explain the result. The
preview needs no prior Treasury work. `navigation/LIFECYCLE_MAP.md` connects the
current requirement, task, check, handoff and later policy change. Chapters 5–14 add controls when design,
coordination, release, state, teamwork or measurement make them useful.

The four Parts cover Chapters 1–4, 5–7, 8–10 and 11–14. Appendix A is a connected
worked solution. Appendix B develops practical research-to-decision questions.
`SOLUTION_NAVIGATION.txt` and `EXERCISE_COVERAGE.json` map their entry points.
The separate `practice/team_operations/Advanced_Learning_Protocol.pdf` retains
the optional delayed human learning protocol. That study requires Linux, the
same host and boot, at least 24 hours between its specified phases, independent
reviewers and controlled prior-answer exposure. It is not a prerequisite for
the ordinary Chapters 13–14 route. No human learning outcome has been measured.

The current CP06/CP07 records carry the complete pending-review register. The
schema revision does not approve the requirements, design or operator copy.
`reader_side/schemas/REVIEW_SCHEMAS_V2.md` explains the current paths and the
migration from retained historical records. Distinct original fixture IDs and
receipts remain intact; their dates and internal versions describe their own
observations. Do not silently substitute an old receipt for current source.


## Choose your chapter and starting state

```bash
python3 -B reader_start.py doctor
python3 -B reader_start.py show 1
python3 -B reader_start.py new 1 --destination ../my_treasury_lab
```

Use `-B` when inspecting the extracted release so Python does not create import
bytecode caches there. The commands above leave authored input files unchanged;
your separate study copy is where exercise edits and generated evidence belong.

`show N` displays the input state, prerequisite, candidate/reference commands,
editable paths, expected starter result and pending decisions for every chapter.
`new N` creates a separate study copy from an unchanged release starter. Chapter
1 gets its deliberate routing defect; later chapters keep the delivered
incomplete candidates. No earlier solution or approval is silently installed.
For cumulative work, continue your existing copy and use `show`, rather than
creating a fresh copy for every chapter. See `navigation/RECOVERY.md` for stale
receipts and a non-destructive reset. An existing destination is never replaced.

Chapter 10's `complete_technical_learning.py` can recognize the technical
exercise completed by a correct alternative source. Its result does not grant
or replace the original fictional release decision. See `README_CP10.md`.

The optional practice materials support the original sequence:

| Material | Use |
| --- | --- |
| `practice/native_journey/` | Separate specification-first CSV journey with actual native files, attempts, checks and explicitly recorded outcome |
| `practice/semantic_integration/` | Separate two-head integration exercise with an actual semantic conflict |
| `practice/native_client/` | Installed OpenCode with a local model: setup, bounded Chapter 1 repair, recorded failures and MCP host route |
| `practice/agent_workflow/` | Retained CP01 observation, client preflight, boundary and context/skill exercises |
| `practice/csv_export/` | Runnable bounded CSV feature, protected selection behavior and actual implementation record |
| `practice/lifecycle/` | Separately approved fictional operator feature through archive, policy history and incident recovery |
| `practice/verification_tools/` | Actual Hypothesis and Bandit checks with failing controls |
| `practice/ai_review/` | Actual critic findings and a sealed small-case comparison |
| `practice/orchestration/` | Executable Chapter 7 task graph, bounded workers, durable attempts and explicit recovery |
| `practice/harness_engineering/` | Treasury harness candidates, development traces, held-out evaluation and source-bound reuse |
| `practice/harness2_upstream/` | Pinned official Harness² deterministic demo; Python 3.12 or 3.13 |
| `practice/mcp_cli/` | Pinned official SDK and standard-library CLI on one read-only policy task |
| `practice/sdd/` | Fixed-format fidelity comparison, fresh Spec Kit scaffold and actual externally dispatched generation/review |
| `practice/production_controls/` | Representative compatibility checks and production-control decisions |
| `practice/workflow_cost/` | Prospective activity, usage and decision records with overlap and unknown-value checks |
| `validation/NATIVE_HOST_COLLECTION.md` | General evidence collector used by the named-client route; receipt validation does not itself establish task success |
| `practice/team_operations/` | Team agreement, review capacity, onboarding, experiment and measurement sheets |

Read the origin and limitations of each receipt. The historical CP01 ChatGPT
repair discloses prior reference-solution exposure. The d4 CSV worker and SDD
generator were given bounded fresh tasks without the author reference answers;
their inspection records describe what they actually read. Shared filesystem
access is not process isolation. Those historical observations are ChatGPT collaboration. The separately retained
native route uses installed OpenCode 1.19.3 with a pinned local Qwen3-4B model. Its
setup, failed attempts, interventions and resulting checks have their own dated
records under `practice/native_client/`. The old preflight remains an accurate
record of its earlier environment. Codex CLI, Claude Code and GitHub Copilot
remain unobserved contrasts; no paired performance comparison is claimed.

## Run the Chapter 7 orchestration and harness examples

These optional practice examples read the current Treasury intent and source
without accepting or modifying the original chapter candidates. For the Treasury
harness, first extract a fresh, unchanged copy of this edition and run from that
copy's `companion/`; keep completed cumulative work in its existing copy. An edited
delegation plan is intentionally rejected by the harness source pins. The upstream
demo requires Python 3.12 or 3.13, so check the interpreter before its command.
Choose new output directories outside `repo/` and `reader_side/`:

```bash
python3 practice/orchestration/run_demo.py --output ../oh_runs/orchestration_01
python3 practice/harness_engineering/run_experiment.py --output ../oh_runs/harness_01
python3 --version
python3 practice/harness2_upstream/run_demo.py --output ../oh_runs/upstream_01
```

The first command actually dispatches local subprocess workers, joins independent
tasks and records bounded retry, timeout, dependency failure and interruption
scenarios. Resume preserves completed attempts; uncertain interrupted attempts
require reconciliation. Its optional argv adapter can wrap an installed client,
and the default demo uses deterministic Python workers. A separate d4 run at
`practice/sdd/observed_external_agent_20261021/run/` dispatches actual ChatGPT
generation and an independent reviewer through `external_worker.py`. Its durable
state ends at `WAITING_HUMAN` after the two bounded tasks. Read the separate run
and bridge instructions before interpreting or reproducing that route.

The Treasury harness experiment keeps the correct Decimal router unchanged.
It compares response configuration, tool use and a deliberately memorizing
candidate, then evaluates the adopted composition on separate held-out inputs.
The fixed composer receives development trace summaries and the public output
contract. The author-known fixtures and shared local filesystem do not provide
adversarial isolation or a model-performance estimate.

The upstream demo runs unmodified first-party code from the pinned official
Harness² commit, using Python 3.12 or 3.13. Its editor makes a scripted repair
and its selector can compute the source ledger's arithmetic. Read its README
before interpreting the correct selected results. The three commands in this
section make zero model calls and keep full local evidence. The separately
recorded external SDD run is not one of these scripted commands. Neither route
authorizes the original CP07 decisions or unblocks its implementation task.

Focused tests can be run independently:

```bash
python3 -m unittest discover -s practice/orchestration -p 'test_*.py' -v
python3 -m unittest discover -s practice/harness_engineering/tests -v
```

Author maintenance of current documentation and protected checker sources is
recorded in the d4 change evidence. A learner must not refresh the owner-side
manifest to make an unauthorized edit pass. The integrity mechanism detects
changes against its baseline; it does not establish a host security boundary.

## Begin the Chapter 1 exercise

The packaged router already conforms to the inherited routing contract. To
reproduce Chapter 1's original repair exercise, prepare a new full working copy
from the book-package root:

```bash
python3 companion/reader_side/tools/prepare_chapter01.py --destination chapter01_work
cd chapter01_work
python3 reader_side/tools/run_acceptance.py \
  --output reader_side/evidence/CH01_BASELINE_RESULT.json
```

The destination must be new and outside the source `companion/`. Preparation
changes only the new copy's `repo/src/treasury/routing.py`. The seven owner-side
cases initially produce three passes, two failures and two errors. Repair only
that router, then run `python3 reader_side/tools/run_acceptance.py` again; the
result is saved as `reader_side/evidence/CH01_ROUTING_RESULT.json`. Copy
`reader_side/templates/CH01_REVIEW_TEMPLATE.md` to
`reader_side/evidence/CH01_REVIEW.md` and record your review.

After reviewing a passing repair, preserve it and adopt the fixed reference
router for the later chapter exercises, in this same working copy:

```bash
cp repo/src/treasury/routing.py reader_side/evidence/CH01_REVIEWED_ROUTER.py
cp reader_side/evidence/CH01_ROUTING_RESULT.json \
  reader_side/evidence/CH01_REVIEWED_RESULT.json
cp reader_side/reference_solution/routing.py repo/src/treasury/routing.py
python3 reader_side/tools/run_acceptance.py \
  --output reader_side/evidence/CH02_ROUTING_BASELINE.json
```

Later discovery/specification gates check this exact reference source digest
to enforce their no-routing-change scope. An alternative implementation may
pass the seven cases and still have a different digest; the preserved source
and evidence retain your work. Do not change the owner-side digest files to
make a later stage pass. Continue Chapters 2–14 in this same working copy.

## Start with the shared regression suite

```bash
python3 reader_side/tools/run_checks.py
```

The runner discovers all acceptance and regression tests once in this shared
repository, checks protected integrity before and after, and runs stable faulty
and correct controls. It writes `reader_side/evidence/INTEGRATED_CP01_CP14_RESULTS.json`.

**Expected for the supplied teaching starters:** the regression suite passes;
the current candidate workflow fails because several learner artefacts are
intentionally wrong. CP10's current dossier is `NOT_RUN` until a rehearsal is
nominated. CP11 policy/history readiness is reported separately and initially fails with its intentional starter. CP12 incident recovery is `NOT_RUN` until a current incident session is nominated. These are separate fields in the report. Fixing the learners'
candidates does not remove the protected faulty controls. CP13 protocol/knowledge
readiness is `NOT_RUN` until a transfer session is nominated; human learning
remains pending regardless of the automated gate result.
CP14 measurement review is NOT_RUN until its session is nominated; actual human
effort, billing and field economics remain unknown even after a machine pass.

To require the regression suite and the current Chapters 1–9 candidate workflow
to pass (the existing option keeps this meaning):

```bash
python3 reader_side/tools/run_checks.py --require-candidates
```

The older `run_checks_cp08.py` and `run_cp09_checks.py` names now call this same
runner. They do not run a second code branch or add overlapping test counts.

## Chapter exercises and edit scopes

| Chapter | Candidate / stage | Dedicated gate |
| --- | --- | --- |
| 1–2 | Routing contract and portable workspace | `run_acceptance.py` and `scope_guard.py` |
| 3 | Discovery assessment | `discovery_gate.py` |
| 4 | Behavior specification | `spec_gate.py` |
| 5 | Two design prototypes and proposed ADR | `architecture_gate.py` |
| 6 | Knowledge packet and context-audit skill | `knowledge_gate.py` |
| 7 | Delegation plan and handoff | `planning_gate.py` |
| 8 | Presentation increment and implementation report | `implementation_gate.py` |
| 9 | Independent verification exercise and review | `verification_gate.py` |
| 10 | Review dossier, exact merge candidate, local artifact release and rollback rehearsal | `rehearse_release.py` and `release_gate.py` |
| 11 | Versioned policy, persistent history, retry identity and evidenced SQLite migration | `evolution_gate.py` and `policy_history_cli.py` |
| 12 | Causal hypothesis review, wrong-state-path reproduction and preserved-state recovery | `rehearse_incident.py` and `incident_gate.py` |
| 13 | Different-cause transfer evidence, versioned knowledge and a proposed delayed human pilot | `rehearse_transfer.py`, `learning_gate.py` and `learning_pilot.py` |
| 14 | Observed local attempts, distinct scenario outcomes, explicit costs and proposed tool-pilot decision | `rehearse_measurement.py` and `measurement_gate.py` |

Gate scripts live in `reader_side/tools/`. Each chapter README gives its
reference commands. The combined editable-file inventory exists to support all
chapters; it does not grant every exercise access to all those files.

Before starting Chapter 8, capture the current working copy's baseline. This
preserves any legitimate changes already made in earlier chapters:

```bash
python3 reader_side/tools/scope_guard.py --chapter CP08 \
  --capture reader_side/evidence/CP08_EDIT_BASELINE.json

# Make only the Chapter 8 candidate changes, then check them.
python3 reader_side/tools/implementation_gate.py \
  --scope-baseline reader_side/evidence/CP08_EDIT_BASELINE.json
```

Keep the baseline under reader/CI control. Do not recapture it after an
out-of-scope edit to erase the difference. Capture refuses to overwrite an
existing baseline; use a new filename for a genuinely new exercise session.
For Chapter 9 use profile `CP09`, a separate baseline and the same option on
`verification_gate.py`. That profile permits only the Chapter 9 candidate and
review record; changing the Chapter 8 source requires returning to Chapter 8.
For Chapter 10 use profile `CP10` and `release_gate.py`; only
`repo/engineering/release/release_dossier.json` is editable in that exercise.

Without `--scope-baseline`, a dedicated gate can check current behavior and
protected integrity but cannot establish the actual before/after edit scope.
The file-policy check is educational; real isolation requires controls outside
the candidate's process and filesystem authority.

## Review the actual cross-chapter workflow

```bash
# Demonstrate all protected worked-example stages without changing your files.
python3 reader_side/tools/integration_gate.py --reference

# After repairing the chapter exercises, review their current combined state.
python3 reader_side/tools/integration_gate.py \
  --output reader_side/evidence/CURRENT_WORKFLOW_RECEIPT.json

# Later, require the earlier passing evidence still to match every input.
python3 reader_side/tools/integration_gate.py \
  --receipt reader_side/evidence/CURRENT_WORKFLOW_RECEIPT.json
```

The gate checks the current discovery, specification, proposed design/ADR,
knowledge, planning, implementation and independent-verification artefacts.
It also passes the **actual Chapter 8 `build_explanation()`** through Chapter
9's independent case expectations and independently checks `status_label`.
The original Chapter 9 faulty wrapper remains a separate teaching control.

Receipts bind the reviewed source, reports, earlier-stage artefacts, router,
adapter, policy, oracle and protected-checker manifest by SHA-256. A comment-only
source change invalidates old evidence even when the selected behavior stays
the same. A receipt records observed checks; it is not a human approval.

A repaired Chapter 8 alone is insufficient if earlier/current chapter artefacts
still fail. The final status is `PASS_REVIEW_GATE_ONLY`. The Chapter 7 plan
continues to show its requirements and architecture decisions pending and T07-04 blocked;
Chapter 8's separate local teaching work order does not execute that task.
No gate grants payment, merge or release authority.

## Add the Chapter 10 review and release rehearsal

Read `README_CP10.md` for the dossier fields, protected mock PR discussion and
decision records. The dossier consumes evidence from the same cumulative lab;
it does not replace the earlier exercises with a separate application.

After completing the earlier candidates, capture a CP10 edit baseline and
create a new rehearsal:

```bash
python3 reader_side/tools/scope_guard.py --chapter CP10 \
  --capture reader_side/evidence/CP10_EDIT_BASELINE.json
python3 reader_side/tools/rehearse_release.py \
  --output reader_side/evidence/CP10_CURRENT

# Repair only the dossier; retain the originally captured baseline.
python3 -B reader_side/tools/complete_technical_learning.py \
  --rehearsal reader_side/evidence/CP10_CURRENT \
  --scope-baseline reader_side/evidence/CP10_EDIT_BASELINE.json \
  --output reader_side/evidence/CP10_TECHNICAL_COMPLETION.json
```

The book, command card and `README_CP10.md` use these same names. Prepare the
session once, then continue with its files. For another attempt, use a new suffix
consistently for the baseline, rehearsal and results. A different correct
implementation may reach `TECHNICAL_LEARNING_COMPLETE` while the unchanged nested
release assessment remains `FAIL` / `NOT_AUTHORIZED`. Use the actual candidate
source identity and accurate technical references. If no applicable fictional
decision exists, set both `review_decision_id` and `release_decision_id` to JSON
`null`, and keep all four authority claims false. Stale inputs, incorrect behavior,
wrong artifact identity, scope violations and self-issued decisions still block
technical completion. This outcome does not measure human competence or approve
a release. `README_CP10.md` supplies the explanation rubric.

Every rehearsal uses a new directory. It creates a local Git repository with
real base, head and merge-candidate identities, materializes the merge tree,
runs selected checks there, packages exact current and previous artifacts, and
rehearses selection of the previous artifact and restoration of the current
one. It has no remote and makes no deployment. Keep the generated session
under reader control; it contains the evidence the dossier refers to.

For a protected worked example that leaves the learner files unchanged:

```bash
python3 reader_side/tools/rehearse_release.py \
  --output reader_side/evidence/CP10_REFERENCE --reference
python3 reader_side/tools/release_gate.py \
  --rehearsal reader_side/evidence/CP10_REFERENCE \
  --candidate reader_side/reference_solution/ch10/release_dossier.json
```

`--reference` installs the earlier reference artifacts only inside the new
disposable copy. It does not repair the current working copy or authorize
another implementation. The protected synthetic owner decisions cover the
known presentation-source digest. A different source needs a new applicable
owner decision even if its selected behavioral checks pass.

A completed rehearsal reports `READY_FOR_DOSSIER_REVIEW`. A passing dossier
reports `PASS_LOCAL_RELEASE_REHEARSAL_ONLY`, with distinct CI, review, local
release and rollback fields. Moving the recorded base or head, changing the
checked source, substituting an artifact, omitting a mandatory resolution or
using self-approval blocks the gate. Real human acceptance, production release
and payment authority remain false; Chapter 7's pending decision remains
pending. The local receipt is not a signed attestation or a SLSA-level claim.
For a current source covered by an applicable protected fictional decision,
optionally require the original release disposition as well:

```bash
python3 reader_side/tools/run_checks.py \
  --release-rehearsal reader_side/evidence/CP10_CURRENT --require-release
```

This optional combined requirement needs a `WORKING_CANDIDATES` session; a
protected reference rehearsal cannot certify the current working source. It is
expected to fail for an unapproved alternative even when its technical exercise
is complete. Keep that refusal instead of changing the authorization fixture.

## Add Chapter 11 policy evolution without rewriting history

Read README_CP11.md. Its separate work order permits only
repo/src/treasury/policy_history.py and repo/engineering/evolution/policy_delta.json.
The new SQLite exercise retains BR-001/v1 at EUR 5,000 and introduces an explicit
BR-001/v2 at EUR 3,000. The old router and its input contract remain unchanged.
The synthetic legacy database is a new teaching fixture, not a previously
operated database recovered from earlier chapters.

Capture profile CP11 before editing and use evolution_gate.py --output NEW_DIR
with --scope-baseline. The gate preserves actual databases, fresh-process logs,
and a hash-bound EVOLUTION_RESULT.json. Its success is
PASS_POLICY_EVOLUTION_REVIEW_ONLY. The shared --require-evolution option requires
the current Chapters 1–9 workflow and CP11; it does not imply CP10 release
readiness. CP10 remains NOT_RUN unless a rehearsal is supplied. CP11 source
changes stale prior CP10 sessions; CP10 presentation artifacts exclude the new
policy-history module and cannot authorize policy-v2 release. CP07 remains
pending/blocked and payment/release authority stays false.

## Investigate Chapter 12 without erasing incident history

Read `README_CP12.md`. CP12 permits only the deployment configuration and
incident review under `repo/engineering/operations/`. It reuses the unchanged
CP11 `PolicyStore` in fresh local Python processes. A path-only control isolates
the seeded deployment fault; recovery then validates explicit state guards on
new copies. Original and incident SQLite ledgers remain separate and retained.
Incident-only decisions require owner reconciliation, even after local service
selection is restored.

Capture profile `CP12` before editing. `rehearse_incident.py --output NEW_DIR`
records the current-source incident; `incident_gate.py --rehearsal DIR --output
NEW_DIR --scope-baseline FILE` evaluates the repair. A separate `--reference`
mode demonstrates protected worked examples. The gate's success is
`PASS_INCIDENT_RECOVERY_REVIEW_ONLY`. `run_checks.py --incident-rehearsal DIR
--require-operations` requires the actual current CP01–CP09, CP11 and CP12
candidates; it does not imply CP10 release acceptance, production recovery or
incident closure. Telemetry is standard-library process JSON, not executed
OpenTelemetry SDK/exporter instrumentation. Source/configuration changes stale
applicable earlier receipts.

## Grow skills and knowledge with Chapter 13

Read `README_CP13.md` and `reader_side/learning/PROTOCOL.md`. CP13 permits only
the transfer review and team knowledge JSON records under
`repo/engineering/learning/`. The same PolicyStore service now uses the correct
ledger with an unexpected active-policy rollback. Actual fresh-process
evidence distinguishes this cause from CP12's wrong-path fault and validates
recovery on a new copy without rewriting history.

Capture profile `CP13` before editing. `rehearse_transfer.py --learning-session
CP12_DIR --output NEW_DIR` records the transfer case; `learning_gate.py
--transfer-session DIR --output NEW_DIR` reviews the current candidates. A
separate reference mode cannot certify the current source. The combined
`run_checks.py --incident-rehearsal CP12_DIR --transfer-session CP13_DIR
--require-learning` requires actual current CP01–CP09, CP11, CP12 and CP13
machine readiness and the same bound CP12 session. It does not imply CP10
release acceptance or human competence.

The human protocol seals immediate, delayed-retention and transfer answers in
that order. Real delay eligibility uses the owner's actual wall/monotonic
clock on the same Linux boot; synthetic calibration uses explicitly fictional
clock/rater fixtures. Two raw reviewer profiles remain independent and any
adjudication is additive. The four 0–3 dimensions and 24-hour interval are
provisional teaching choices. Human-trial completion, rubric validation and
learning claims remain pending in this automated delivery. Editing CP13
candidates invalidates applicable earlier CP10 source receipts; no learning
artifact grants release, reconciliation or CP07 authority.

## Measure outcomes and choose a tool stack with Chapter 14

Read `README_CP14.md` and `reader_side/measurement/PROTOCOL.md`. Only the two
interpretation JSON records under `repo/engineering/measurement/` are editable.
The rehearsal executes actual CP13 commands in a disposable copy, preserving
reject, repair, repeated-green, stale-receipt and refresh attempts. Raw local
process duration is measured; human effort, billing and real owner acceptance
remain unknown. One exact final synthetic owner acceptance supplies the
scenario denominator, regardless of repeated green attempts.

Capture profile CP14 before editing. `rehearse_measurement.py
--incident-rehearsal CP12_DIR --transfer-session CP13_DIR --output NEW_DIR`
records the workflow. `measurement_gate.py --measurement-session DIR --output
NEW_DIR --scope-baseline FILE` reviews the interpretation. The shared
`--require-measurement` option also requires the nominated current CP12/CP13
sessions and all prior current readiness. It binds the original CP13 seed and
the refreshed child separately; both derive from the same CP12 identity.

Finite Decimal scenario calculations include every attempt, review and rework,
use one currency and report an undefined cost per accepted outcome when the
denominator is zero. GO/CHANGE/STOP sensitivity is conditional; the actual
decision remains CHANGE to collect missing field evidence. Dated tool
documentation is not a live benchmark. An unfilled field-telemetry template and
protocol support a future pilot without inventing people, bills or results.
CP10 release, CP07 approval, incident reconciliation and human/rubric validation
remain separate and ungranted.

## Reproduce the complete integration validation

From the book-package root, run:

```bash
python3 scripts/validate_integrated_lab.py
python3 scripts/validate_chapter10_lab.py
python3 scripts/validate_chapter11_lab.py
python3 scripts/validate_chapter12_lab.py
python3 scripts/validate_chapter13_lab.py
python3 scripts/validate_chapter14_lab.py
```

It works on temporary copies, validates the faulty starters, installs all
protected reference artefacts through the chapter scopes, runs the complete
repaired workflow, and challenges stale evidence, presentation labels and
protected inputs. Delivered candidates and historical snapshots remain intact.
The complete author package keeps this edition's validation records under
`revision_d8/`. Consult `RUNTIME_MATRIX.json` for each actual run, its status and
validation scope. Historical d7 records retain their own exact inputs and results. A standalone companion does
not include all author-package validators or archive evidence. The CP10 validator
covers the rehearsal, stale identities, decision boundaries and artifact rollback.
These scenario checks are separate from the shared unit-test count.

The earlier editorial-review archive retains the original chapter snapshots;
this lean revision package contains the canonical cumulative lab and its
checkpoint history. It uses the Chapter 6 knowledge model required by Chapter
7. The core offline checks make no third-party-dependency or live-agent claim.
Optional practice evidence is separately labelled and versioned.

## Continue the separately approved fictional lifecycle

`practice/lifecycle/README.md` starts a distinct teaching continuation. Its
requirements, technical, operator-copy and release decisions are explicit
fictional records bound to the actual candidate. The route adds an operator
view, packages it into the Chapter 10 archive, exercises the Chapter 11 policy
store and carries the same ledger into Chapter 12 incident recovery. It preserves
the original CP07 plan as pending. Use this route to see the lifecycle connect;
do not substitute its fictional decisions for real project acceptance.
