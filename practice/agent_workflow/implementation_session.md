# Make the agent's contribution inspectable

Use this card with the CP08 work order. The authoring record for CP01 is a worked
example of visible contribution; it is not a measured CP08 run. The CP08 task
remains a local presentation experiment, separate from blocked T07-04.

## Before delegation

Read `reader_side/implementation/WORK_ORDER_CP08.md` and the selected behavior
cases. Predict the first wrong field for `4999.99`. The correct router can remain
green while the wrapper invents approval, policy version and benefit claims.
Capture the current candidate and report identity, preserve a fresh red result,
and retain the owner-side edit baseline before editing:

```bash
python3 reader_side/tools/scope_guard.py --chapter CP08 \
  --capture reader_side/evidence/CP08_EDIT_BASELINE.json
python3 reader_side/tools/implementation_gate.py
```

Keep the baseline unchanged. If continuing an already repaired lab, do not
pretend it is an unsafe initial state; use a separate untouched exercise copy if
you need the original defect.

## Give the task, then watch the boundary

“Fix `src/treasury/explanation_alpha.py` and its
`engineering/implementation/implementation_report.json` only. Preserve routing,
BR-001/v1, the EUR 5000 boundary, the no-payment notice and pending ADR-005.
First report the observed mismatch. Propose the smallest patch, show commands and
results, and stop at READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED. Do not change tests or
claim user value, acceptance or release.”

Before allowing a command, identify whether it reads, writes, installs or calls an
external service. Ask why a newly proposed capability is necessary. Actual runtime
restrictions must be configured outside this prompt.

## Retain contribution, observation and judgment separately

| Record | Include | Do not infer |
|---|---|---|
| Inputs and context | Task, source revision, loaded rules/skills, prior solution exposure | A file was loaded just because it exists |
| Actions | Exact commands, tool requests, rejected actions, edits and interventions | A proposed command ran successfully |
| Candidate | Before/after source and actual diff, report identity | All changed behavior is covered by selected cases |
| Verification | Raw exit codes/output, candidate and oracle identities, scope baseline | An agent-authored summary is an independent test |
| Disposition | Remaining questions and the real reviewer/owner decision, if any | Model agreement creates human acceptance |

Run the retained candidate through the owner-side gate and inspect its actual diff:

```bash
python3 reader_side/tools/implementation_gate.py \
  --scope-baseline reader_side/evidence/CP08_EDIT_BASELINE.json
python3 reader_side/tools/run_checks.py
```

The shared suite's regression success is different from this candidate's gate.
The later cumulative integration gate can still fail if earlier exercise
candidates remain wrong.

Use the versioned `implementation-report/v2` contract for new records. It
separates `fixture_origin: SYNTHETIC_TEACHING_CASE` from `execution_mode`, which
is `OFFLINE_DETERMINISTIC` or `ACTUAL_AGENT_CLIENT`. A real agent can work on a
synthetic task; these facts do not conflict. The offline form uses
`observed_run_ref: null`. An actual-client form must bind the companion-relative
path and SHA-256 of its `agent-client-observation/v1` record. The gate checks
the candidate and transcript identities, actual client metadata, timestamps,
outcome and `CLIENT_ATTEMPT_ONLY_NOT_ACCEPTANCE` claim scope. Unavailable client name, client version or model identity uses the nonempty
marker `UNKNOWN_NOT_EXPOSED`, as required by this schema. The marker records
missing information; it is not a model name or evidence of a particular release.
Nullable usage, billing and human-effort fields remain null when unavailable.

See `reader_side/schemas/REVIEW_SCHEMAS_V2.md`,
`reader_side/reference_solution/v2/implementation_report.json` and
`reader_side/tools/provenance_core.py` for the maintained fields. Existing v1
reports with `live_agent_run: false` remain explicit offline compatibility
records. Keep a historic receipt unchanged; issue a v2 record for a new attempt.
Evidence binding establishes consistency among the retained files, not the
external authenticity of a self-reported client identity. Human review,
architecture approval and release remain distinct decisions.

Unknown model identity, bill, token count and human effort stay unknown. Process
durations describe only the recorded interval. Failed attempts remain in the
record, and a fresh comparison starts from the same original source rather than
the previous agent's solution.
