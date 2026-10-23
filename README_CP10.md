# Chapter 10 — Review, integrate and release with explicit decisions

Run these commands from the same `companion/` working copy used for Chapters
1–9. Python's standard library and a local Git installation supporting
`git merge-tree --write-tree` are required. No remote, account or network is
used. The exercise retains BR-001/v1 and the EUR 5,000 routing boundary.

## Start with your current change

Your job is to connect your checked Chapter 8 presentation source to its actual
merge, artifact and recovery evidence. Complete the Chapters 1–9 candidates
first. Under CP10, edit only `repo/engineering/release/release_dossier.json`.
The commands below capture that boundary and create a fresh rehearsal. A
complete technical submission reaches `TECHNICAL_LEARNING_COMPLETE` through
the command in the technical-completion section. The existing release gate
separately reports whether a protected fictional decision covers this exact
source. Retain both results for Chapter 11.

You can complete the technical exercise with your own correct implementation.
You do not need to reproduce the reference program's bytes. This endpoint
records the exercise checks; it is not a measured learner competence result.

## Evidence, decisions and authority

This chapter has one editable candidate:

`repo/engineering/release/release_dossier.json`

The dossier connects exact CI evidence, mock PR discussion resolutions, an
independent review decision, a separate release decision and a rollback
rehearsal. Green checks do not create an acceptance or release decision.
The protected fixture decisions concern only the known Chapter 8 presentation
source and `LOCAL_SYNTHETIC_PRESENTATION_EXPERIMENT`.

The gate reports `ci_status`, `readiness`, `review_decision`,
`local_release_decision` and `rollback_status` separately. Its strongest status
is `PASS_LOCAL_RELEASE_REHEARSAL_ONLY`. The upstream architecture decision
remains pending, Chapter 7 T07-04 remains blocked, and real human acceptance,
real release authorization and payment authorization remain false.

## Continue with the current working candidates

First complete and review the earlier chapter exercises. This check must pass
before using their current artifacts for Chapter 10:

```bash
python3 reader_side/tools/run_checks.py --require-candidates
python3 reader_side/tools/scope_guard.py --chapter CP10 \
  --capture reader_side/evidence/CP10_EDIT_BASELINE.json
python3 reader_side/tools/rehearse_release.py \
  --output reader_side/evidence/CP10_CURRENT
```

The book, command card and this guide use the same current-route names. Run the
capture and preparation commands once for that session; continue with its
existing files when switching among these instructions. For another attempt,
choose a new suffix consistently for the baseline, rehearsal and result files.
The rehearsal destination must be new. It creates a disposable full source
copy, a local Git repository, an actual merge commit and a separate materialized
copy of that exact commit. It does not repair the caller's candidates. A
successful rehearsal stops at `READY_FOR_DOSSIER_REVIEW`.

Inspect the initially faulty dossier:

```bash
python3 reader_side/tools/release_gate.py \
  --rehearsal reader_side/evidence/CP10_CURRENT \
  --scope-baseline reader_side/evidence/CP10_EDIT_BASELINE.json \
  --output reader_side/evidence/CP10_INITIAL_REVIEW.json
```

The faulty dossier omits required checks, leaves mandatory discussion threads
unresolved, cites author self-approval, lacks a release authorization, chooses
the current artifact as its rollback target and overclaims human acceptance
and execution of the blocked Chapter 7 task. These are expected failures even
when the named CI checks are green.

Read `reader_side/release/mock_pr.json` and `owner_decisions.json`. Repair only
the dossier, preserving the original before-edit baseline. The protected
worked-example dossier is `reader_side/reference_solution/ch10/release_dossier.json`.
Its fields show the expected references; they do not give the learner authority
to invent a reviewer, close a thread or approve a release.

Continue to the technical-completion section for your implementation. The two
commands below additionally assess release: an uncovered alternative is expected
to receive a release refusal, even after its technical component is complete.

```bash
python3 reader_side/tools/release_gate.py \
  --rehearsal reader_side/evidence/CP10_CURRENT \
  --scope-baseline reader_side/evidence/CP10_EDIT_BASELINE.json \
  --output reader_side/evidence/CP10_REVISED_REVIEW.json

python3 reader_side/tools/run_checks.py \
  --release-rehearsal reader_side/evidence/CP10_CURRENT --require-release
```

The combined requirement needs the current Chapters 1–9 workflow, the current
Chapter 10 dossier and a `WORKING_CANDIDATES` rehearsal to pass. Without a
nominated rehearsal the shared runner reports Chapter 10 readiness as
`NOT_RUN`. A regression pass alone does not claim that the dossier passed.

## Complete the technical exercise with your own correct source

When the independent selected checks pass for a byte-different implementation,
use its actual `candidate_source_sha256` from `CP10_CURRENT/rehearsal.json`.
Keep the required check, artifact, rollback and discussion references accurate.
For a source outside the protected owner's fixed decision, leave
`review_decision_id` and `release_decision_id` as JSON `null`, and retain all four
authority claims as `false`. This honestly records unissued decisions. It does
not request a new approval or alter the historical fixtures.

Then run, using the CP10 baseline captured **before** editing the dossier:

```bash
python3 -B reader_side/tools/complete_technical_learning.py \
  --rehearsal reader_side/evidence/CP10_CURRENT \
  --scope-baseline reader_side/evidence/CP10_EDIT_BASELINE.json \
  --output reader_side/evidence/CP10_TECHNICAL_COMPLETION.json
```

The result has two distinct outcomes:

| Field | Completion condition and meaning |
| --- | --- |
| `status: TECHNICAL_LEARNING_COMPLETE` | Fresh checks of the current source and actual merge/archive, correct technical dossier links, preserved CP10 edit scope and successful local rollback. A reference rehearsal cannot complete your working-candidate task. |
| `release_assessment` | The unchanged release gate's complete verdict. An uncovered alternative still has `status: FAIL` and `local_release_decision: NOT_AUTHORIZED`; missing decisions, self-approval and stale decisions do not become release authorization. |

A stale input, incorrect behavior, wrong artifact identity, out-of-scope edit,
self-issued approval or an authority overclaim prevents technical completion.
The documented pending-decision branch permits the three findings caused by an
unissued source-specific decision only when both decision references are `null`.
It never converts the nested release refusal into a pass. Keep the original
verdict and request a separately controlled applicable decision for any real
release. Do not use `--require-release` as the completion criterion for an
unapproved alternative.

To finish the learning submission, also explain why the current merge passes,
which case would reveal a wrong boundary, what the previous artifact restores,
and why this evidence gives no release authority. These explanations are a
reader/reviewer rubric, not facts inferred automatically from the command.
Two different authored implementations and negative controls are exercised in
`reader_side/extended_tests/test_technical_completion.py`.

## Inspect the protected worked example without repairing your files

The original delivered earlier-stage starters are deliberately incomplete. A
separate reference rehearsal makes the worked example available immediately:

```bash
python3 reader_side/tools/rehearse_release.py --reference \
  --output reader_side/evidence/CP10_REFERENCE_REHEARSAL

# Stable negative control; expected FAIL.
python3 reader_side/tools/release_gate.py \
  --rehearsal reader_side/evidence/CP10_REFERENCE_REHEARSAL \
  --candidate reader_side/release/unsafe_dossier.json

# Protected correct dossier; expected PASS_LOCAL_RELEASE_REHEARSAL_ONLY.
python3 reader_side/tools/release_gate.py \
  --rehearsal reader_side/evidence/CP10_REFERENCE_REHEARSAL \
  --candidate reader_side/reference_solution/ch10/release_dossier.json
```

The reference option installs earlier protected solutions only inside the new
copy. The verdict explicitly reports `PROTECTED_REFERENCE`; it cannot satisfy
the combined `--require-release` requirement for the caller's current source.

The synthetic decision covers the exact protected CP08 source SHA-256
`4cae28f8db65a185fd5faed74f564af48207aa45f27f3febb79edba0d57e87a3`.
A different implementation can pass the selected checks and still require a
different owner decision. Do not edit the protected authorization fixture to
make an uncovered source pass.

Use the technical-completion route above to finish the engineering task while
preserving the release refusal.

## What the rehearsal actually checks

The local repository has four refs: `prior`, `target`, `candidate` and
`merge_candidate`. The candidate introduces the actual Chapter 8 presentation
source. The target advances independently with a synthetic review note. A real
two-parent merge commit combines those changes; the tool recomputes its tree
and materializes the commit with `git archive`.

| Evidence ID | Actual check and output |
| --- | --- |
| `CI-MERGE-001` | Recorded parents/tree and materialized file hashes; `evidence/merge.json` |
| `CI-ROUTING-001` | Seven owner acceptance cases on the materialized merge; `evidence/acceptance.json` |
| `CI-INTEGRATION-001` | Existing Chapters 1–9 integration gate on the materialized merge; `evidence/integration.json` |
| `CI-ARTIFACT-001` | Eight selected independent smoke cases on the extracted exact artifact; `evidence/artifact.json` |

These are the named local CI checks. The shared regression suite is run
separately; the rehearsal does not recursively invoke it. All CI records bind
the same base/head/merge identities, source hash, integration receipt and
artifact digest. A dirty Git worktree does not replace the recorded commit.

`artifacts/current.zip` is packaged deterministically from the committed
Treasury source. Sorted entries, fixed ZIP metadata and uncompressed bytes make
its digest reproducible for that commit. The gate rebuilds those bytes from
Git and rejects artifact substitution.

The mock PR is executable review input. Mandatory `THREAD-10-01` requires the
actual routing, integration and artifact checks; `THREAD-10-02` requires a
verified previous-artifact selection and restoration. Protected independent
resolution records are `RESOLUTION-10-01` and `RESOLUTION-10-02`. The dossier
cannot close either thread with a self-declared boolean. `REVIEW-10-ACCEPT`
belongs to `reviewer-a`; `RELEASE-10-LOCAL` belongs to the separate
`release-owner`. Explicit reject, self-approval and deny fixtures exercise the
negative paths.

## Try a semantic integration failure

The optional independent exercise in `practice/semantic_integration/README.md`
uses two changes to different files. Both checked heads pass the same output
contract; their actual conflict-free merge fails because both layers add the
same required notice. A one-file repair restores the contract. The command
retains the two heads, combined failure, repair, source identities and check
results without changing the protected CP10 release history.

## Reproduce a stale-base block

Use a disposable rehearsal and preserve its existing evidence. Move only its
local target ref, leaving the candidate head unchanged:

```bash
git -C reader_side/evidence/CP10_REFERENCE_REHEARSAL/repository \
  branch -f target candidate
python3 reader_side/tools/release_gate.py \
  --rehearsal reader_side/evidence/CP10_REFERENCE_REHEARSAL \
  --candidate reader_side/reference_solution/ch10/release_dossier.json
```

The result must fail with `STALE_BASE`. Moving `candidate` separately is caught
as `STALE_HEAD`. A source-byte change after CI is also stale, including a
comment-only change. Create a new rehearsal for a new review session; do not
rewrite old checks to make them appear current.

## Rollback is an actual local selection rehearsal

`artifacts/previous.zip` contains the previous core explanation adapter: it
preserves routing, reasons, policy, notice and benefit status but does not add
Chapter 8's `status_label`. Its bytes come from the exact `prior` commit and
remain separately identified from the current presentation artifact.

The tool selects `CP10-CURRENT`, selects `CP10-PREVIOUS`, runs the prior
artifact's core smoke cases, restores `CP10-CURRENT`, and runs its presentation
smoke cases. `selection_log.jsonl` records those three actual changes;
`selected_artifact.json` identifies the restored artifact. The gate rechecks
artifact digests, selection history and both smoke results. A rollback-ready
claim or a pointer to the wrong artifact fails.

This exercises artifact selection and behavior in local temporary processes.
It does not exercise production deployment, data rollback, incident response
or a policy-history replay. Later chapters address their separate concerns.

## Reproduce the packaged validation

From the book-package root:

```bash
python3 scripts/validate_chapter10_lab.py
```

The default first-run directory is `build/chapter10_validation`. Every run
requires a new output directory; existing evidence is preserved. For another
run, choose a fresh path explicitly:

```bash
python3 scripts/validate_chapter10_lab.py --output build/chapter10_validation_02
```

The validator uses disposable copies, repairs earlier candidates there,
captures the Chapter 10 edit boundary, rejects the faulty dossier, accepts the
correct one, runs the combined current-source requirement, and challenges
stale refs/source, wrong CI identities, review/authority claims, artifact
substitution and rollback restoration. It reads actual test counts from the
shared runner JSON and verifies that the delivered source stayed unchanged.

Known author-created Python runs locally. Protected records and reader-held
evidence must remain outside the learner's write scope. These checks are not
an arbitrary-code sandbox or cryptographic proof of a person's identity.

## Later policy-evolution scope

Chapter 11 adds a separate policy-history experiment. CP10 freshness binds its
candidate/delta/catalog/context inputs, so changes invalidate an older session.
The CP10 artifact deliberately excludes policy_history.py: its synthetic owner
decisions remain limited to the presentation experiment. A new CP10 pass does
not approve policy v2 or migrate a database; policy_evolution_release_authorized
remains false. Use README_CP11.md for the independent policy/history gate.
