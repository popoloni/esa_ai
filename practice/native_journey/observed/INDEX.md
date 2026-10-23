# Recorded native CSV observation

**Status: OPEN_PARTIAL_BUDGET_EXHAUSTED.** The useful final CSV feature passes
independent checks. A fresh native check after the last cleanup and an accurate
native handoff remain missing. Four of four allowed client invocations were
used, totaling 1,274.40 client wall seconds of 2,700 allowed. The server stopped
cleanly.

## Start with the useful result

The actual [specification](project/spec.md), [plan](project/plan.md) and
[implementation](project/api.py) were written by the installed native client.
[CURRENT_CONTRACT.md](project/CURRENT_CONTRACT.md) supplies the existing authored
fictional consumer decision. See the actual
[CSV output](recorded/visible_result/alice_open.csv) and
[JSON output](recorded/visible_result/alice_open.json) for Alice's open orders:
`A1` is included; Bob's `B1` and Alice's closed `A2` are excluded. The multiline
note and customer value survive. The separately
[authored teaching specification](../teaching/CSV_SPEC.md) is an editorial
derivative with [explicit provenance](../teaching/PROVENANCE.json), not native
output.

| Invocation | Actual result | Evidence |
|---|---|---|
| 01 | Failed read, weak spec/plan, undefined formatter failure, then an incomplete repair with unsupported formats falling through. | [Raw events](recorded/attempt_01/stdout.txt), [snapshot](recorded/project_after_01/api.py), [independent review](recorded/review_after_01/REVIEW.json) |
| 02 | Corrective prompt produced the useful persisted spec and plan. A literal `other` guard still violated the general unsupported-format rule; repeated unchanged failure ended in an authored bounded stop. | [Guidance](recorded/continuation_02/TASK_PROMPT.txt), [raw events](recorded/attempt_02/stdout.txt), [stop](recorded/attempt_02/AUTHOR_STOP_REQUEST.json) |
| 03 | Native edit generalized refusal; seven native behavior checks passed. The handoff also claimed an unperformed cleanup. | [Raw events](recorded/attempt_03/stdout.txt), [checked source](recorded/project_after_03/api.py), [handoff review](recorded/HANDOFF_REVIEW_AFTER_03.json) |
| 04 | Native edit removed the unreachable statement. The final text claimed a check, but no new check event occurred. | [Raw events](recorded/attempt_04/stdout.txt), [final source](project/api.py), [handoff review](recorded/HANDOFF_REVIEW_AFTER_04.json) |

The [final independent review](recorded/independent_final_review/REVIEW.json)
passed 17 selected behavior, scope and nonempty-file checks and the unchanged
seven-case supplied checker. [Content review](recorded/CONTENT_REVIEW.json)
separately assesses meaning and identifies the source-attribution wording that
the teaching derivative clarifies. The independent result does not supply the
missing native event.

## Audit or reproduce

Read the [declared protocol](recorded/preparation/PROTOCOL.json),
[initial prompt](recorded/preparation/TASK_PROMPT.txt),
[actual event index](recorded/EVENT_INDEX.json),
[runtime identity](recorded/RUNTIME_PREFLIGHT.json),
[host and versions](recorded/HOST_AND_SERVER_VERSION.json),
[configuration finding](recorded/CONFIGURATION_FINDING_01.json),
[interpretation limits](recorded/INTERPRETATION_LIMITS.json),
[budget disposition](recorded/INITIAL_BUDGET_DISPOSITION.json),
[server finish](recorded/server_01/FINISH.json) and
[detailed outcome](recorded/OUTCOME.json). Each attempt directory contains raw
JSONL output, stderr, before/after manifests, exact invocation receipt and native
session export. Exports may contain earlier session history; the per-invocation
stream identifies the events from that call. Every continuation retains its
prompt, effective configuration and intervention record.

The full source snapshots after each invocation remain in
`recorded/project_after_01/` through `recorded/project_after_04/`. The final
`project/` is byte-for-byte identical to `recorded/project_after_04/`.
Historical absolute paths in records are unchanged evidence; use the
[README](../README.md) and helpers for new locations. No model weights, client
binaries or private client databases are shipped here.

The first request set agent temperature 0.2 but omitted the provider model
capability; server diagnostics showed 0.8. Continuations corrected the
capability and logged 0.2. The author supplied the final plan's direct-formatter
choice and later semantic repair guidance. This is a supervised observation,
not an autonomous benchmark or OP05 architectural exploration.

**Remaining action:** in a separately budgeted future continuation, obtain an
actual native check on the final bytes and an accurate handoff. Preserve this
episode and its open status. No fifth call was made. Earlier R06/R08
observations and the R17 human-validation dependency retain their original
outcomes.
