# One approved teaching change, from a decision to recovery

This continuation answers the question left open by the deliberately blocked
`PLAN-007/v1`: **what happens after the relevant owners accept a bounded change?**
It follows the same Treasury explanation through the actual CP08 repair, the
existing CP10 Git and artifact rehearsal, CP11 policy history and CP12 recovery.
It also gives the operator useful words instead of another machine status code.

The owner decisions here are explicitly fictional, author-supplied teaching
fixtures. They are not records of actual people accepting a production change.
The historical v1 plan and its pending requirements, architecture and copy review
remain unchanged. They are the negative control for this exercise.

## Run the complete continuation

From the companion directory, with Python and local Git installed:

```sh
python3 practice/lifecycle/run_lifecycle.py --output ../lifecycle_run_01
```

Use a new directory outside the companion for every run. The command creates an
isolated cumulative worked-example workspace. It never repairs the learner's
original candidates or overwrites an earlier result. It prints a checkpoint after
each completed stage and records partial progress in `LIFECYCLE_RESULT.json`.
The expected final status is `PASS_APPROVED_TEACHING_LIFECYCLE`.

Start reading with `evidence/OPERATOR_STORY.txt`, then inspect the records that
explain a decision you want to challenge. The important outputs are:

| Output | What to inspect |
| --- | --- |
| `TECHNICAL_TRANSITION.json` | Both the fictional requirements decision and technical decision apply to the contract and exact candidate identity. |
| `TRANSITION_NEGATIVE_CONTROLS.json` | A changed status label, missing requirements decision, other candidate, other architecture, escalated authority or changed candidate bytes is refused. |
| `IMPLEMENTATION.json` | The actual CP08 starter hash changes to the existing repair; the new operator module has its own exact identity. |
| `logs/operator_source_review.stdout.log` | Expected wording and boundary behavior are checked outside the candidate module. |
| `release/rehearsal.json` | Real local Git commits, merge tree, archive identities and current/previous/current selections. |
| `OPERATOR_RELEASE.json` | The released archive contains the exact approved view and passes the operator cases; the previous archive lacks the new module. |
| `POLICY_OPERATIONS_TRANSITION.json` | A separately scoped fictional decision permits the policy/history and recovery exercise. |
| `evolution/EVOLUTION_RESULT.json` | The actual CP11 implementation passes its selected persistent-history checks. |
| `incident/steps/` and `recovery/steps/` | Actual fresh-process observations and retained SQLite state, not a fabricated incident narrative. |
| `OPERATOR_STORY.json` | Before/after output and historical/current/fault/recovery views for the same EUR 4,000 input. |
| `EVALUATION.json` | Benefit and comprehension remain unmeasured, separately from product output. |

## Read the owner decision before the implementation

`PLAN-007/v2-TEACHING` explicitly supersedes the proposed task scope for this
fictional continuation. The old task proposed an edit to `architecture/direct.py`.
The accepted design already exists, so the revised task reuses it and permits the
actual `explanation_alpha.py` repair plus a new `operator_view.py`. Reporting the
old direct-adapter edit as executed would be false; the new plan says what changed.

The requirements owner accepts the fixed behavior and operator contract. The
technical owner selects direct and accepts the bounded implementation. Both
decisions bind `operator_contract.json` and its exact candidate identity. The
validator checks those bindings before the writer acts, checks the implemented
bytes afterwards, and repeats the check at the end. A maker cannot create a valid
transition by writing `APPROVED` in the plan. These local checks are not an
authentication service or a sandbox against an actor who can rewrite the checker.

The current cumulative lab still validates its historical pending snapshots. Its
`T07-04 = BLOCKED` result refers to `PLAN-007/v1`. The new transition is separately
identified and validated; no earlier green result is relabeled as an approval.

## Follow the useful behavior

For EUR 4,000.00 under v1, the new view explains:

```text
Send to the standard queue.
EUR 4,000.00 is below the EUR 5,000.00 routing threshold.
Policy: BR-001/v1 (routing threshold EUR 5,000.00)
Next: Continue with the standard queue's review procedure.
Payment approval is separate from this queue recommendation.
```

At exactly EUR 5,000, it recommends human review and explains that the amount
equals the threshold. An invalid amount produces a correction action. The view
uses the supplied router decision; a contradictory route or unknown policy makes
it stop rather than silently substitute a different decision. It retains input
precision, so EUR 4,999.999 is not misleadingly displayed as EUR 5,000.00.

The legacy wrapper and original SQLite records retain `benefit_status` because
their protected fixtures and history were written with that field. The versioned
operator projection omits it. Experimental benefit belongs in `EVALUATION.json`,
where it remains an unvalidated hypothesis. Passing wording tests establishes
specified output on selected cases; it does not establish operator comprehension.

## Follow the same code and state

The `--teaching-operator` option in the existing CP10 rehearsal adds the new module
in the candidate commit, so the real previous archive lacks it. Default CP10
behavior is unchanged. The original CP10 owner fixture still covers its exact CP08
producer. A separate fixed fictional review/release decision covers the complete
operator artifact, and the independent view checks run on its extracted bytes.
This is a local artifact selection, not a hosted deployment.

The CP10 archive excludes `policy_history.py`, as it did before. The separately
scoped policy/operations decision permits the next local exercise with that exact
CP11 source. The CP12 rehearsal's first events create a v1 historical request,
activate v2 and create a new request in **one original ledger**. Those are the
Chapter 11 story's actual records. Later events select the wrong ledger and then
recover the original. We do not invent a second history just to make the prose fit.

The operator view uses each saved decision's policy snapshot. The old request
still explains v1 after activation; the new request explains v2 and human review.
The wrong ledger visibly explains v1 when current v2 was expected. Recovery keeps
the original old and new identities. Both ledgers remain preserved; the incident
ledger is quarantined pending a reconciliation decision. Restoration does not
automatically resolve every business consequence or close an incident.

## Inspect or extend the exercise

The source module is `operator_view.py`; the independent expected outputs are in
`operator_cases.json`. The transition, requirements, technical, review/release and
policy/operations decisions are separate files so their different roles can be
read without editing the candidate. They are fixed fixtures. The run command never
regenerates an owner decision to match changed candidate bytes.

To propose new wording or behavior, first describe the new contract and the
applicable owner decision in your own exercise. A changed module correctly fails
the present decision's identity check. Real release authority, actual operator
research and production operations need their own evidence and responsible people.
