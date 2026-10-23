# Follow a native CSV change through its actual checks

[Home](../../README.md) · [Practice catalogue](../README.md) · [Chapter routes](../../navigation/CHAPTER_ROUTES.md)

For the later passing guided run, including virtual environments and complete
commands, see the [reproduction guide](../native_client/REPRODUCE_GUIDED_CSV.md).
That new observation does not change the historical outcome recorded below.

This optional route uses the existing [CSV exercise](../csv_export/README.md)
and one installed OpenCode client. The useful result is a CSV response for the
same actor-visible, status-filtered orders as the existing JSON response. It
does not need the Treasury chapters or their release vocabulary.

The route is deliberately small: write a useful specification, record a short
design and task plan, edit the presentation, run the behavioral check, interpret
the result, and stop with a handoff. This is an authored specification-first
workflow. It is **not a new execution of Spec Kit** and does not change the
historical [native Spec Kit observation](../sdd/NATIVE_ROUTE_D8.md).

**Recorded outcome: `OPEN_PARTIAL_BUDGET_EXHAUSTED`.** The installed client
persisted a useful specification and plan and implemented a working CSV
response. Its third invocation ran the seven selected contract checks
successfully. Its fourth invocation removed an unreachable statement, then
claimed the check had run without a new check event. The final bytes pass
separate independent verification, but the complete native check and accurate
handoff target remains open. Four of four allowed invocations were used;
1,274.40 of the 2,700 allowed client wall seconds were used. The attempt limit
ended the episode, and the server was stopped. No fifth invocation is claimed.

The [observation index](observed/INDEX.md) connects that outcome to the actual
files, raw events, failed attempts and author interventions. In particular,
[the final project](observed/project/spec.md) and the
[project actually checked by the native client](observed/recorded/project_after_03/api.py)
are retained separately.

## Task and decision boundary

`CURRENT_CONTRACT.md` in the CSV starter is the task authority. It already
contains the fictional owner decision `CSV-CONSUMER-01`: the consumer is a
machine importer and values, including formula-like text, are preserved
literally. The new specification must name that source. Spreadsheet viewing,
HTTP authentication and deployment remain separate decisions. Neither the
native client nor a passing check supplies real customer approval.

The allowed implementation files are `api.py` and optional `presenter.py`.
This separate observation also permits new `spec.md` and `plan.md` teaching
records. Selection, fixtures, the existing contract and the external checker
remain unchanged. The supplied prompt does not include a reference solution
or the checker source. Its author has seen the prior exercise and checker;
this is a disclosed teaching observation, not a blind benchmark.

## Read or try the route

To see the observed useful result, run these commands from the companion root.
They inspect the frozen final candidate; they do not invoke a model:

```bash
python3 -B practice/native_journey/observed/project/demo.py \
  --format csv --actor alice --status open
python3 -B practice/csv_export/checks/check.py \
  --candidate practice/native_journey/observed/project
```

The output includes `A1`, preserves its customer `Acme, North` and multiline
note, and excludes Bob's `B1` and Alice's closed `A2`. The JSON response retains
the same selected order and values. See the actual
[CSV output](observed/recorded/visible_result/alice_open.csv) and
[JSON output](observed/recorded/visible_result/alice_open.json). The check returns
`PASS_SELECTED_CONTRACT` for seven selected cases. A separate review passed
17 selected behavior, scope and nonempty-file checks; substantive document
quality was assessed separately in [CONTENT_REVIEW.json](observed/recorded/CONTENT_REVIEW.json).
These counts are not a coverage claim, user study or deployment approval.

The normal offline exercise remains available immediately:

```bash
cp -R practice/csv_export/starter ../csv_attempt_01
python3 -B practice/csv_export/checks/check.py --candidate ../csv_attempt_01
```

The starter intentionally refuses four CSV checks while its existing JSON,
unsupported-format and unchanged-input checks pass. Keep that result before
editing. Implement only the permitted presentation files, then repeat the
same command. `PASS_SELECTED_CONTRACT` is a technical result under the declared
local contract. Record what was checked and what remains unknown.

To collect a new installed-client observation, first follow the pinned setup
in [native_client/README.md](../native_client/README.md). The observed setup is
Linux x86-64, OpenCode 1.19.3, Qwen3-4B Q4_K_M and llama.cpp b11799 on a CPU.
The helper uses an existing runtime outside the companion; no model weights
or client binaries are included. New versions or platforms need their own
observations.

Choose unused paths, then prepare without inference:

```bash
python3 -B practice/native_journey/prepare_observation.py \
  --companion . --runtime ../esa_native_runtime_01 \
  --project ../esa_native_csv_01 --state ../esa_native_csv_state_01 \
  --evidence ../esa_native_csv_evidence_01/preparation
```

Inspect `PROTOCOL.json`, `TASK_PROMPT.txt`, the initial checks and the effective
client configuration. The configured tools may edit only the named files and
run the exact external check command. These are client application rules, not
OS isolation. The effective agent also retains its internal tool-output path
exception. A localhost model endpoint does not prove that every component
makes no other network connection.

In a separate terminal start the retained server launcher with a fresh log
directory and the same context as the configuration:

```bash
python3 -B practice/native_client/run_local_model_d8.py \
  --runtime-root ../esa_native_runtime_01 \
  --evidence ../esa_native_csv_evidence_01/server_01 \
  --ctx-size 16384 --max-runtime-seconds 3600
```

Verify readiness and runtime identities as described in the native-client
guide, then start the actual client capture:

```bash
python3 -B practice/native_journey/run_observation.py \
  --preparation ../esa_native_csv_evidence_01/preparation \
  --output ../esa_native_csv_evidence_01/attempt_01
```

Each invocation has a 900-second outer bound. The observation budget allows at
most four invocations and 2,700 seconds of cumulative client wall time; stop
at the first limit. A follow-up must preserve the earlier task and outcome and
use a new task file and output directory. `steps=12` is a last-step instruction
in this pinned client, not a mechanical tool-call limit. Stop the local server
after the task. A new run can produce different edits or fail.

The original protocol called that timer inference wall time. The recorder
measures the client invocation, including startup and tools; it does not isolate
inference time or total author effort. The first configuration requested agent
temperature 0.2 but omitted the model's temperature capability, so server
diagnostics showed 0.8. The correction and observed 0.2 for the continuation
are retained in [the configuration finding](observed/recorded/CONFIGURATION_FINDING_01.json).
The helper now includes the capability. This change is disclosed, without
attributing quality improvements to it.

## Recover from generated-code failures

A client exit code of zero only means the client stopped normally. Require a
passing supplied contract check and a separate independent review on the final
candidate bytes before calling the implementation successful.

If a small local model deletes the API, invents an undefined helper, or repeatedly
duplicates fragments, preserve that failed project and its trace. Start a new,
explicitly guided attempt from an untouched starter instead of accumulating
repairs on corrupted code. Keep the same contract and checks.

Useful guidance is to read the existing API and selection dependency first,
preserve the function signature and JSON branch, and add the smallest CSV branch
using Python's standard CSV writer and an in-memory text buffer. Hand-joining
fields does not handle quoted delimiters and embedded newlines. Keep field order,
literal values, authorization/filtering and the empty-result header unchanged.
This is implementation guidance, not an autonomous or blind evaluation; retain
the exact prompt and any added read permissions in the new evidence packet.

Keep selection, fixtures and checkers unchanged. Run the original checker after
the edit, then independently review the final bytes, permitted file scope and
both JSON/CSV demos. Preserve unsuccessful attempts as well as any eventual pass.
Do not replace the shipped intentional starter with a generated answer.

## Evidence and teaching text

The [observation index](observed/INDEX.md) identifies the actual project,
native events, session exports, recorded interventions and independent checks.
The actual native [specification](observed/project/spec.md) and
[plan](observed/project/plan.md) remain byte-for-byte copies. The separately
[authored teaching specification](teaching/CSV_SPEC.md) clarifies the contract
identifier, source attribution and examples. Its [provenance](teaching/PROVENANCE.json)
names those editorial changes; it was never written into the native project.

The final native handoff is retained as an unsupported check claim, not quoted
as the reviewer's conclusion. The next native completion criterion is precise:
in a separately budgeted continuation, observe a real check on the final bytes,
then obtain a handoff that accurately names that check and its limits. Preserve
this four-invocation episode and its open disposition. Independent passing
checks cannot retrospectively supply a missing native event.

The existing Chapter 1 native repair and Chapter 4 Spec Kit episodes retain
their original partial outcomes. This separate journey does not make their
missing native checks or artifacts appear retroactively.
