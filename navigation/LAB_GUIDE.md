# Cumulative lab guide

[Home](../README.md) · [Navigation](README.md) · [Chapter routes](CHAPTER_ROUTES.md) · [Recovery](RECOVERY.md)

For software installation, source readiness and the complete first-exercise sequence, start with [Getting started](GETTING_STARTED.md). Run the prerequisite and starter checks before following the exercise steps below.

Run commands from the repository root (the directory containing [reader_start.py](../reader_start.py)), not from this navigation directory. Create a separate study copy with the [home-page quick start](../README.md#start-here), then continue Chapters 1–14 in that copy.

## On this page

- [Chapter 1 repair and continuation](#begin-the-chapter-1-exercise)
- [Shared regression suite](#start-with-the-shared-regression-suite)
- [Chapter scopes and edit baselines](#chapter-exercises-and-edit-scopes)
- [Cross-chapter verification](#review-the-actual-cross-chapter-workflow)
- [Later chapters](#continue-through-chapters-1014)

## Begin the Chapter 1 exercise

Inside the study copy created by the quick start, run:

```bash
python3 reader_side/tools/run_acceptance.py \
  --output reader_side/evidence/CH01_BASELINE_RESULT.json
```

The seven owner-side cases initially produce three passes, two failures and two errors.
Repair only [the Treasury router](../repo/src/treasury/routing.py), then run
`python3 reader_side/tools/run_acceptance.py` again; the
result is saved as `reader_side/evidence/CH01_ROUTING_RESULT.json`. Copy
[reader_side/templates/CH01_REVIEW_TEMPLATE.md](../reader_side/templates/CH01_REVIEW_TEMPLATE.md) to
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

The older [run_checks_cp08.py](../reader_side/tools/run_checks_cp08.py) and [run_cp09_checks.py](../reader_side/tools/run_cp09_checks.py) names now call this same
runner. They do not run a second code branch or add overlapping test counts.

## Chapter exercises and edit scopes

| Chapter | Candidate / stage | Dedicated gate |
| --- | --- | --- |
| 1–2 | Routing contract and portable workspace | [run_acceptance.py](../reader_side/tools/run_acceptance.py) and [scope_guard.py](../reader_side/tools/scope_guard.py) |
| 3 | Discovery assessment | [discovery_gate.py](../reader_side/tools/discovery_gate.py) |
| 4 | Behavior specification | [spec_gate.py](../reader_side/tools/spec_gate.py) |
| 5 | Two design prototypes and proposed ADR | [architecture_gate.py](../reader_side/tools/architecture_gate.py) |
| 6 | Knowledge packet and context-audit skill | [knowledge_gate.py](../reader_side/tools/knowledge_gate.py) |
| 7 | Delegation plan and handoff | [planning_gate.py](../reader_side/tools/planning_gate.py) |
| 8 | Presentation increment and implementation report | [implementation_gate.py](../reader_side/tools/implementation_gate.py) |
| 9 | Independent verification exercise and review | [verification_gate.py](../reader_side/tools/verification_gate.py) |
| 10 | Review dossier, exact merge candidate, local artifact release and rollback rehearsal | [rehearse_release.py](../reader_side/tools/rehearse_release.py) and [release_gate.py](../reader_side/tools/release_gate.py) |
| 11 | Versioned policy, persistent history, retry identity and evidenced SQLite migration | [evolution_gate.py](../reader_side/tools/evolution_gate.py) and [policy_history_cli.py](../reader_side/tools/policy_history_cli.py) |
| 12 | Causal hypothesis review, wrong-state-path reproduction and preserved-state recovery | [rehearse_incident.py](../reader_side/tools/rehearse_incident.py) and [incident_gate.py](../reader_side/tools/incident_gate.py) |
| 13 | Different-cause transfer evidence, versioned knowledge and a proposed delayed human pilot | [rehearse_transfer.py](../reader_side/tools/rehearse_transfer.py), [learning_gate.py](../reader_side/tools/learning_gate.py) and [learning_pilot.py](../reader_side/tools/learning_pilot.py) |
| 14 | Observed local attempts, distinct scenario outcomes, explicit costs and proposed tool-pilot decision | [rehearse_measurement.py](../reader_side/tools/rehearse_measurement.py) and [measurement_gate.py](../reader_side/tools/measurement_gate.py) |

Gate scripts live in [reader_side/tools/](../reader_side/tools/). Each chapter README gives its
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
[verification_gate.py](../reader_side/tools/verification_gate.py). That profile permits only the Chapter 9 candidate and
review record; changing the Chapter 8 source requires returning to Chapter 8.
For Chapter 10 use profile `CP10` and [release_gate.py](../reader_side/tools/release_gate.py); only
[repo/engineering/release/release_dossier.json](../repo/engineering/release/release_dossier.json) is editable in that exercise.

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

## Continue through Chapters 10–14

Use the dedicated guides for session creation, exact commands and expected results. Capture the chapter's edit baseline before changing its candidates and preserve receipts from earlier attempts.

| Chapter | Guide | Distinction to retain |
| --- | --- | --- |
| 10 | [Release rehearsal](../guides/README_CP10.md) | Technical completion can pass without an applicable fictional release decision. |
| 11 | [Policy evolution](../guides/README_CP11.md) | Preserve earlier decisions; policy changes can stale prior release receipts. |
| 12 | [Incident recovery](../guides/README_CP12.md) | Restore selected state without erasing incident history or granting reconciliation. |
| 13 | [Learning and transfer](../guides/README_CP13.md) | The synthetic lab is separate from the optional delayed human study. |
| 14 | [Measurement](../guides/README_CP14.md) | Local process observations are not human-effort or billing measurements. |

For stale evidence, follow [recovery](RECOVERY.md). For a separately approved **fictional** continuation across Chapters 8–12, see the [lifecycle exercise](../practice/lifecycle/README.md). It does not approve the original pending Chapter 7 plan.
