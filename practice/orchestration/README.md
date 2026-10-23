# Run a small orchestrator

[Home](../../README.md) · [Practice catalogue](../README.md) · [Chapter routes](../../navigation/CHAPTER_ROUTES.md)

This Chapter 7 extension executes a dependency graph using real local worker
processes. Two workers inspect snapshots of the cumulative Treasury lab, and a
third consumes their results. A separate branch stops at a human decision.

The supplied workers are **deterministic Python programs**. The controller is
real scheduling and recovery code, but the demonstration is not a multi-LLM
benchmark, a named coding-client trial or a production orchestration service.
There are no model calls, model credentials, network calls or paid APIs in the
default exercise. Python 3.10 or later is the declared language floor; the
observed environment and actual checks are in `observed_v2/OBSERVATIONS.json`.
The earlier `observed/` run remains historical evidence; version 2 adds the
reviewed output-path and retained-file collision controls.

## 1. Run the complete experiment

First choose the controller route in `../../navigation/CHAPTER_ROUTES.md`.
Read the permissions and budget in the supplied plan and the recovery rules in
this guide before dispatch. The demonstration has its own task identities and
does not execute the cumulative learner plan or accept its architecture decision.
From the **companion root**, use a new destination:

```bash
python3 practice/orchestration/run_demo.py --output ../orchestration_run_01
python3 -m unittest discover -s practice/orchestration -p 'test_*.py' -v
```

The destination must not exist. Outputs belong outside `repo/` and
`reader_side/`, whose contents the demonstration fingerprints before and after
execution. A second experiment needs a different output directory. Existing
evidence is never silently replaced. Both the direct controller and the demo
refuse symlink ancestors and destinations inside those original trees before
creating a run directory.

Open `../orchestration_run_01/OBSERVATIONS.json`. It links eight observations:

| Directory | What actually executes | Expected outcome |
|---|---|---|
| `01_success` | Two investigators, then a synthesizer; resume after completion | Three completed tasks; two concurrent workers observed; resume adds no attempts |
| `02_human_blocked` | The same investigators and synthesizer, then a human boundary | `WAITING_HUMAN`; proposed implementation has zero attempts |
| `03_retry` | First process deliberately exits 7; a second process completes | Both attempts retained, within a limit of two |
| `04_failed_dependency` | An upstream process fails | Dependent task never starts |
| `05_timeout` | Two deliberately slow processes | Both time out; no third attempt |
| `06_interrupt_resume` | Actual SIGINT during routing inspection; two resume requests | Unapproved retry stays uncertain; explicit idempotent retry completes |
| `07_stale_input` | Complete a task, modify its disposable input, request resume | Resume refused because identity changed |
| `08_escaping_output` | Supply a response path containing `..` | Rejected before dispatch |

Assertions in the demo check the expected outcomes. A demo finishing with
`PASS_LOCAL_DETERMINISTIC_SCOPE` means that these selected observations behaved
as expected, including the deliberate failures. It does not mean every worker
invocation returned zero.

## 2. Inspect the Treasury workflow

The demo copies exactly these existing source files into each case's `inputs/`:

| Original cumulative source | Snapshot | Use |
|---|---|---|
| `repo/src/treasury/routing.py` | `routing.py` | Execute the supplied router for five representative amounts |
| `reader_side/intent/INT-001.md` | `intent.md` | Inspect the input-validation intent and retained EUR 5,000 boundary |
| `reader_side/reference_solution/delegation_plan.json` | `protected_plan.json` | Observe the protected example's pending and blocked decisions |

The supplied `policy` worker reads the intent and the protected reference plan.
The `routing` worker executes the copied module for `4999.99`, `5000.00`,
`5000.01`, `0` and `NaN`. They have no dependency on one another. The `synthesis`
worker starts only after both processes have returned valid, fingerprinted
results. It verifies those fingerprints before reading their observations.

These are selected observations of the teaching router, not a complete new
acceptance suite. The reference plan is intentionally available to the worker;
this is not a blind evaluation. The experiment neither repairs the learner's
Chapter 7 JSON nor executes its proposed task T07-04. The original protected
T07-03 remains `PENDING_HUMAN`, and T07-04 remains `BLOCKED`.

`02_human_blocked/plan.json` uses its own task IDs, `owner_decision` and
`proposed_implementation`. They illustrate a runtime stop without claiming that
an owner has accepted the earlier architecture. No command in this extension
approves a payment, merges a change, records a real reviewer verdict or deploys.

## 3. Read execution state rather than a completion message

`01_success/run/state.json` contains both the task states and the ordered event
journal. The controller writes them together through a temporary file, flushes
it and atomically replaces the prior state. There is one authoritative journal,
so a separate append-only event file cannot disagree with the task state.

Each attempt has a new directory:

```text
01_success/
  inputs/
  plan.json
  run/
    state.json
    attempts/policy/001/
      request.json
      result.json
      stdout.txt
      stderr.txt
```

The attempt record contains its process ID, full argument array, timestamps,
exit code, outcome and measured elapsed time. Successful result bytes have a
SHA-256 identity. Failed attempts retain their output as well. A `TASK_STARTED`
event establishes that a process was started; `TASK_COMPLETED` additionally
requires exit zero and a valid result envelope. Neither grants human acceptance.

## 4. Run the controller directly

After running the demo, execute its plan into another new directory:

```bash
python3 practice/orchestration/orchestrator.py \
  --plan ../orchestration_run_01/01_success/plan.json \
  --inputs ../orchestration_run_01/01_success/inputs \
  --output ../orchestration_manual_01

python3 practice/orchestration/orchestrator.py \
  --plan ../orchestration_run_01/01_success/plan.json \
  --inputs ../orchestration_run_01/01_success/inputs \
  --output ../orchestration_manual_01 --resume
```

The independent example plan is also at `examples/treasury_plan.json`.
`max_parallel` bounds running processes. Each worker has `timeout_seconds` and
`max_attempts`; two attempts means the initial attempt plus at most one retry.
Retry is allowed only when the plan explicitly declares the task idempotent.
The declaration is an engineering claim the owner must substantiate, not proof
the controller can infer from a prompt.

`max_wall_seconds` is a deadline measured from run creation and includes time
between sessions. It is not reset by resume. A completed-only resume checks
identities and returns the retained completion without dispatching work, even
after that deadline. Unfinished work remains subject to it. The example budgets
are small teaching values, not production recommendations.

The process output limit bounds collected stdout/stderr and the accepted JSON
response size. It is polled, so a fast process can briefly overshoot it. This is
not a filesystem quota or a restriction on every file a worker can create.

## 5. Recover an interrupted attempt deliberately

The demo sends an actual SIGINT after the policy worker completes while the
routing worker is still running. The controller terminates its tracked worker
process groups and records `UNCERTAIN` for interrupted work. Inspect:

```text
06_interrupt_resume/state_interrupted.json
06_interrupt_resume/state_reconciliation_required.json
06_interrupt_resume/run/state.json
```

A normal `--resume` refuses to infer success or silently repeat the uncertain
attempt. `--resume --retry-interrupted` permits a new attempt only if the task is
declared idempotent and has attempt budget remaining. In this experiment the
policy worker stays at one attempt; routing retains an interrupted first
attempt and a completed second attempt; synthesis then runs once.

No duplicate-effect guarantee follows. A process might act before the
coordinator receives its result. Non-idempotent work must be reconciled with the
external system, and this small controller provides no automatic reconciler.
It does not implement distributed transactions or an exactly-once protocol.

The local advisory lock prevents a second live coordinator from claiming the
same directory. After a dead coordinator, an old `RUNNING` task becomes
`UNCERTAIN`. If its recorded worker PID may still be alive, automatic retry is
refused. This conservative check can require manual investigation, including
after PID reuse. A leftover `state.json.new` also requires inspection rather
than silent deletion. The observed recovery is cooperative SIGINT; sudden
power loss, SIGKILL and arbitrary corrupt state were not validated.

## 6. Attach a command adapter for an installed agent client

The controller's adapter is an argument array, never a shell command string.
The default is:

```json
["{python}", "{worker}", "--request", "{request}", "--response", "{response}"]
```

`--worker-script PATH` selects another Python wrapper implementing the same
file contract. Alternatively, set `adapter_argv` in a **new plan/run** to a
reviewed executable's arguments. The four permitted substitutions occupy whole
arguments: `{python}`, `{worker}`, `{request}` and `{response}`. There is no
shell interpolation and no `shell=True`. A wrapper can translate the request
into the installed client's input and translate its observed response into the
following envelope:

```json
{
  "task_id": "routing",
  "status": "COMPLETED",
  "summary": "The worker's observed result",
  "client": "Record the actual client and version",
  "model": "Record the actual model when exposed"
}
```

The request supplies the task, attempt number, snapshot directory and paths and
hashes of completed dependency results. The wrapper must write its response
only after the client has finished successfully. A nonzero exit, missing or
malformed JSON, wrong task ID, symlink response or different status fails the
attempt. The alternate-wrapper integration test checks this transport; **no
vendor client or model was run in the retained experiment**.

The configured response path must be a nonempty relative file path. It cannot
use `request.json`, `stdout.txt`, `stderr.txt`, or a child path under those names:
these are reserved for the retained request and process logs. Invalid paths are
refused before any worker is dispatched.

Configure actual client permissions and isolation outside the controller.
Timeouts and process-group termination cannot cancel a remote service or undo a
side effect. A client that detaches children from the process group can outlive
the controller. The adapter inherits the launching environment; review any
credentials it exposes before deliberately using a real client. Do not
interpret the JSON authority text or the snapshot file mode as a sandbox.

## What identity checks establish

Resume compares the plan bytes, input-file inventory, controller and selected
worker-script bytes, Python version and top-level adapter executable bytes. It
also checks completed result identities. Selected input/code/result identities
are rechecked before more work is dispatched during a run. Changes cause a
refusal or invalidation; make a new run to test a changed configuration.

This does not fingerprint a client's entire dependency graph, remote model,
service configuration or environment. It does not protect evidence from an
attacker who controls the coordinator's account and state files. Snapshots are
created read-only for ordinary accidental edits, but their owner can change
their permissions. Output-path checks reject traversal and symlinks in files the
controller consumes; they do not restrict arbitrary worker filesystem access.

## Transfer exercise

Use a disposable copy. Add one worker that checks a different observable
property of the router, then require synthesis to depend on it. Record the new
plan identity and run. Introduce a failure in that worker and verify that
synthesis does not start. Explain why replacing the worker with an LLM changes
the evaluation problem even when the scheduling code is unchanged. Then choose
one operation for which retry would be unsafe and document the reconciliation
evidence it would need.

The focused tests cover process ordering and overlap, blocked human and failed
dependencies, retained retries, attempt/deadline limits, completed and uncertain
resume, changed inputs/plan/code/results, malformed output, symlinks, output
limits and concurrent coordinator exclusion. They exercise a local teaching
controller, not production security or general engineering productivity.

## Connect an externally dispatched model worker

Some hosts expose delegation through their own API rather than a callable local
client executable. `external_worker.py` supports that case through the same
`--worker-script` argument. The controller launches the bridge and creates the
usual request; the bridge writes `DISPATCH.json` inside the attempt directory.
A coordinator reads this file and invokes the actual external agent through its
supported interface. The bridge itself makes zero model calls.

The SDD bundle in `../sdd/create_agent_bundle.py` supplies a complete bounded
generation/review plan. While that controller is running, the coordinator must:

1. Retain the exact dispatch prompt, interface identity and exposed model
   identity. Start a fresh conversation context when the task calls for it.
2. Give the worker the current `request.json`, the supplied input tree, the
   task's required output paths and the current attempt directory. Keep the
   controller inputs unchanged. Inspect which context and tools were actually
   used instead of assuming that an installed skill was loaded.
3. Retain the worker's first artifacts and complete final response text. Record
   actual tool actions separately when the interface exposes them. A saved final
   response is not a complete tool transcript by itself.
4. Write `submission.json` atomically, after every referenced artifact exists.
   Use the exact request digest from `DISPATCH.json` and the actual file hashes.

The submission contract is compact JSON, not a claim of engineering acceptance:

```json
{
  "schema": "treasury-external-worker-submission/v1",
  "task_id": "generate",
  "status": "COMPLETED",
  "request_sha256": "<digest from DISPATCH.json>",
  "summary": "<what this worker actually produced and checked>",
  "provenance": {
    "origin": "external_model_agent",
    "client": "<actual dispatch interface>",
    "model": null,
    "native_cli": false,
    "prior_reference_exposure": "<actual observation or unknown>",
    "context_isolation": "TASK_INSTRUCTION_ONLY_SHARED_FILESYSTEM"
  },
  "artifacts": [
    {"path": "artifacts/spec.md", "sha256": "<actual digest>"},
    {"path": "artifacts/plan.md", "sha256": "<actual digest>"},
    {"path": "artifacts/tasks.md", "sha256": "<actual digest>"}
  ],
  "raw_output": {"path": "RAW_RESPONSE.md", "sha256": "<actual digest>"}
}
```

All artifact paths are relative to that attempt. The bridge rejects stale
request bindings, request changes after dispatch, altered artifact hashes,
missing required artifacts, symlink/traversal paths and files over 1 MiB. It
preserves the claimed dispatch provenance and leaves independent acceptance
pending. The coordinator must supply separate evidence of the actual dispatch:
JSON identity fields alone cannot prove that a model ran. Deterministic adapter
tests use `deterministic_adapter_test` and never count as model observations.

When a submission is missing or malformed, the process fails and the controller
retains that attempt. A new model call may incur another cost or repeat an
external side effect, so the supplied model plan uses one attempt and no
automatic retry. A controller timeout ends this bridge, but the coordinator must
also reconcile or cancel any external agent that is still running. The eventual
review can accept the local evidence for inspection; the human approval task
remains a separate decision.
