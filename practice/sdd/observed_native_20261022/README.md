# Native Spec Kit observation, 22 October 2026

This packet records the actual installed **Spec Kit 1.2.2** command in
**OpenCode 1.19.3**, using the pinned **Qwen3-4B Q4_K_M** model through
**llama.cpp b11799**. The fixed Treasury inputs are synthetic and derived from
the supplied authored `inputs/specification.json` reference contract. This is a
disclosed projection and review exercise, with all five requirements and eight
expected scenarios already present in the fixed inputs.

The first native attempt failed before generating a specification. Its original
error, full native session, complete command expansion, configurations and
unchanged file inventories remain intact. A separately prepared recovery then
returned only a short name and a statement of future intent, with no tool call
or artifact. Its terminal record is also retained. One final, explicitly guided
continuation in that same native session completed the full input-packet read,
then reached its declared outer deadline without generating a specification or
checklist. All 49 project files remained unchanged. **R08 remains partial.**
`OBSERVATION_SUMMARY.json` and `PACKET_STATUS.json` describe the terminal chain;
`PORTABLE_MANIFEST.json` binds every file in this observation packet.

## Read the layers separately

| Directory | Actual role |
| --- | --- |
| `setup/` | Installation commands, exact dependency pins and verification, plus the installed Spec Kit license and distribution metadata. |
| `early_preparation/` | An initial real CLI scaffold and native configuration diagnostics; no model execution. |
| `original_preparations_and_attempt/` | A fresh scaffold and portable helper with separate input reads; diagnostics only. |
| `first_native_attempt/` | Complete original-input bundle, actual named-client invocation, native export and terminal provider failure. The original individual files and full upstream command bodies remain present. |
| `recovery_01/` | Separate fresh scaffold, preserved initialization error/retry, complete compact input packet, repaired configuration, measured preflight and the actual empty task completion. |
| `guided_continuation_01/` | Same native session with one explicit execution request and a separately declared 1,800-second bound. Retains the complete input read, terminal timeout, native export, unchanged history and empty diff. |
| `review_notes/` | Dated preparation findings and a separate terminal follow-up. Earlier claims/hashes remain unchanged; corrections are explicit. |

The recorded paths are the author's actual paths, retained verbatim for
provenance. Reproduce with new directories using [the native route](../NATIVE_ROUTE.md)
and the current helper; do not run a retained task file after editing its paths
and continue to treat its old hash as current.

## What happened in the first native attempt

The actual `speckit.specify` invocation ran from 06:20:45.766 to 06:35:52.533 UTC,
then exited 1 after 906.768 seconds. Its primary request first hit the client's
independent 300,000-millisecond header deadline. An automatic retry then reached
the configured 600,000-millisecond overall deadline. The 1,200-second outer
capture limit was not reached. No primary tool call, feature metadata,
specification or requirements checklist was produced, and the worktree did not
change.

The native log also explicitly records a title-agent stream at 06:20:48.385 UTC,
before the primary stream at 06:20:49.774 UTC. Both used the same local provider
and model. The exported title changed, but there is no completed title usage
receipt. Backend numeric task IDs are not assigned to individual client
purposes by temporal proximity. See `TITLE_ATTRIBUTION_REVIEW.json` and
`OUTCOME_REVIEW.json` inside `first_native_attempt/attempt_01/`.

`EXPANDED_NATIVE_COMMAND_FIRST_OUTPUT.txt` contains the actual expanded **user
command** extracted from the native export. Despite the historical filename,
it is not a generated model answer. The primary first output is the retained
native error event in `stdout.txt`. Zero token/cost fields in an incomplete
session do not establish zero token use or zero total financial cost.

## Why the recovery preparation differs

The full upstream command expands its argument placeholder twice. The recovery
keeps that command unchanged and supplies short explicit arguments pointing to
one complete packet. It compacts JSON whitespace only, verifies equality of all
nine JSON values against their original hashes, and includes the complete router,
specification template, checklist template and unratified constitution. The
general read tool is disabled in this mode; one exact `cat` command supplies the
complete packet without repeated reads or line-prefix overhead. Writes remain
limited to feature metadata, the specification and its requirements checklist.

The repaired configuration names the session, sets both overall and header
deadlines explicitly to 900,000 milliseconds, and includes the upstream schema
metadata before hashing. The new server uses a declared 24,576-token context
and `q4_0` key/value caches. Its actual health, context, memory and identities were
checked before inference; the previous 16,384/`q8_0` lifecycle remains preserved.
These numerical and packaging changes are disclosed, without a performance or
quality comparison.

Actual tokenizer counts are 4,452 for the complete expanded command and 6,698
for the complete input packet. Explicit system/tool, other-tool-result and
aggregate output/history reserves bring the planned total to 23,950 of 24,576
tokens. Those reserves are planning allocations. They are not a captured full
HTTP request or a guarantee that all twelve allowed steps can finish. The outer
capture bound remains 1,200 seconds. `RECOVERY_PREFLIGHT.json` records the checks
and qualifications. The [pinned source diagnosis](../../native_client/setup/runtime_d7/diagnosis/README.md)
explains the separate timeout controls, automatic title and schema insertion.

## The completed response still did not execute the task

The repaired recovery ran from 07:02:07.946 to 07:13:50.275 UTC, for 702.330
seconds. It returned exit 0 and one completed native response, with 6,773 input
tokens and 61 output tokens. The text proposed `treasury-explain` as a short
name, then said it would proceed. Its actual finish reason was `stop`. There
was no tool call, no packet read and no change to any of the 49 project files.
The empty `FINAL_DIFF.patch`, native export, exact first response and controller
review are in `recovery_01/attempt_01/`. The recorder's
`OBSERVED_COMMAND_SUCCESS` status describes its exit status; it does not assert
that the requested specification exists.

That concrete incomplete response motivated one final guided continuation.
The exact appended prompt is retained in
`guided_continuation_01/CONTINUATION_PROMPT_01.txt`. It supplies no draft,
requirement values or owner answers: it asks the same session to execute the
exact allowed input read and then actually write the three permitted artifacts.
The original full command and prior response remain in native history. Pinned
client source and actual `run --help` verify the `--session` continuation path;
the CLI prints this help on stderr. This is additional disclosed assistance,
not a fresh blind trial.

The final continuation prospectively allowed 1,800 seconds, with separate
1,500-second overall/header provider limits and a fresh server using the same
24,576/`q4_0` configuration. No KV state carries over from the stopped server.
The appended instruction adds 120 measured tokens, making the complete planned
budget 24,070 of 24,576. The earlier 702-second cold response made completion
uncertain even with that bound. The 120-token count is the raw appended argument;
the native export retains the CLI's additional quote serialization, which falls
within the declared system/tool/envelope reserve. No later model attempt was
made in this episode.

## The final continuation read the inputs and then timed out

The final native invocation ran from 07:23:02.277 to 07:53:02.360 UTC, for
1,800.083 seconds. At 07:35:31 the model selected the exact permitted
`cat inputs/NATIVE_CONTEXT_BUNDLE.md`. Native output contains all 25,044 bytes,
with SHA-256 `51da598ef2a1d7116869cca05fe637b0120039cf8389f057ab0e6e81b301ae44`,
matching the complete prepared packet without truncation. The step reports
6,964 input and 55 output tokens. A second primary request remained unfinished
when the recorder enforced the outer limit and returned exit 124/TIMEOUT.

No feature metadata, specification or requirements checklist was created.
The final inventory independently matches all 49 before/after file hashes;
`FINAL_DIFF.patch` is empty. The final export retains both prior message parts
exactly unchanged and the disclosed appended prompt, including the pinned
client's quote serialization. There is no new text answer or native clarification
dialogue. A controller deadline after an input read is not an owner decision.

The raw receipt's `origin` still ends with `not_yet_executed`: that label was
copied from the prepared task declaration. Its actual start/end times, native
event, export and timeout record establish execution. Likewise, its generic
`human_review=PENDING` field supplies no review; terminal human review is
explicitly **ABSENT**. The controller note explains both labels without changing
the raw receipt. Its 16 checks establish record consistency, not task completion.

The two completed native steps across the recovered session report 13,737 input
and 116 output tokens, counted once by unique step IDs. The failed earlier
requests and the final unfinished request have missing complete attributable
usage. Native zero fields on incomplete entries and a local client charge of
zero do not establish zero work or total financial cost.

Server shutdown has its own record. After the client cap, the server still had
one processing request and no observed OOM. SIGTERM did not finish within the
retained grace period; the exact verified server child was forcibly stopped.
The child exit -9/launcher 137 differs from the client's timeout 124. The
[closed server lifecycle](../../native_client/setup/runtime_d7/llama_server_03/README.md)
retains that intervention and subsequent absence of both processes. It is not
reported as a clean server exit or a new model attempt.

## Exposure and dependency qualifications

The authored JSON reference contract was an actual fixed input throughout this
route. Earlier broad wording excluding an authored specification or solution
was too broad; it did not describe the packet's full exposure. The current guide
and future helper explicitly distinguish the supplied authored JSON contract
from excluded earlier generated outputs, before/after Markdown exercise answers
and owner responses. The original preparation records and their hashes remain
unchanged. `review_notes/SDD_NATIVE_TERMINAL_FOLLOWUP.json` records the correction
and current future-helper identity without rebinding historical execution.

The native logs also retain unsuccessful background public-registry fetches for
`@opencode-ai/plugin`. Pinned client configuration source explains this loader
activity despite the default-plugin flag. It was nonblocking in the observed
steps. A local inference endpoint does not establish an offline host or OS
containment; no such property is claimed here.

## Review boundary

The original owner questions concern operator vocabulary, accidental payment
approval and actual benefit measurement. No owner answers, ratification or
human acceptance have been supplied. A native provider failure is not a
clarification dialogue or a passed phase gate. A later generated draft must
still be reviewed against all five requirements and eight scenarios, with its
first omissions and unsupported claims retained. A documented clarification
stop can be valid; an invented owner response cannot supply it.

The [independent R08 review](../native_review_20261022/INDEPENDENT_R08_REVIEW.json)
is retained adjacent to this frozen observation packet. It is a separate AI
acceptance audit, not human requirements acceptance. The authored paired exercise
and the separately dispatched ChatGPT generation remain distinct records. A second native framework run is required only for a
measured paired comparison, which this packet does not claim. Client tool
permissions are recorded scope controls; no OS containment is established.
