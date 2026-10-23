# OpenCode Chapter 1 observation — 22 October 2026

**Result:** the second, expressly guided native attempt completed a routing
repair before its outer timeout. Independent assistant review passed the
original seven cases, fourteen additional predeclared cases, and the scope
guard. The two case sets overlap. Human acceptance is pending. The native
client did not complete its planned checker or final summary.

This portable extract records an actual OpenCode 1.19.3 client using Qwen3-4B
Q4_K_M through llama.cpp b11799 on a local loopback endpoint. It is a fresh d7
episode, distinct from the preserved d6 failures. Runtime weights, binaries,
dependencies and client state are deliberately outside this evidence extract.

## Follow the evidence

| Question | Retained record |
| --- | --- |
| What is the final disposition? | [OUTCOME.json](OUTCOME.json) and [independent review](independent_review/REVIEW.json) |
| Which installed client and model? | [CLIENT_IDENTITIES.json](CLIENT_IDENTITIES.json), [version output](version/stdout.txt), and [runtime setup](../../setup/runtime_d7/SETUP_INDEX.json) |
| What were the first output and failed check? | [attempt 01 events](attempt_01/stdout.txt), [session export](attempt_01/native-session.json), and [native acceptance report](independent_review/attempt_01_native_acceptance.json) |
| What assistance changed? | [recovery declaration](RECOVERY_INTERVENTION_02.json), [original prompt](configuration/TASK_PROMPT.txt), and [guided prompt](configuration/TASK_PROMPT_RECOVERY_02.txt) |
| What did the recovery client do? | [attempt 02 events](attempt_02/stdout.txt), [complete session export](attempt_02/native-session.json), [command receipt](attempt_02/RECEIPT.json), and [outcome](attempt_02/OUTCOME.json) |
| What changed in code? | [final diff](independent_review/routing.diff) and [candidate](independent_review/routing.py) |
| Who checked the result? | [independent seven-case report](independent_review/independent_acceptance.json), [additional cases](independent_review/additional_cases.json), [predeclared plan](INDEPENDENT_REVIEW_PLAN.json), and [scope output](independent_review/scope_guard.stdout.txt) |
| What configuration was effective? | [initial effective agent](effective_agent/stdout.txt), [initial config](effective_config/stdout.txt), [recovery agent](recovery_agent_task/stdout.txt), and [recovery config](recovery_config_task/stdout.txt) |
| What usage and timing are actually known? | [USAGE.json](USAGE.json), both attempt receipts, and [bounded server log prefix](server_snapshot/stderr_through_chapter1.txt) |
| What earlier failures remain? | [historical scope](historical_d6/HISTORY_SCOPE.json), the unchanged d6 attempt directories and the original invalid export |
| How can I create my own observation? | [the portable guide](../../README.md), using new directories and generated configurations for your paths |

## Read the outcome precisely

Attempt 01 read the source and ran the acceptance command before making any
edit. The check returned three passes, two failures and two errors, matching
the initial faulty state. An operator interrupted a later model request;
the process ended with exit -2 after 555.556 seconds. No source was changed.

Attempt 02 used a fresh session. Its prompt included the approved intent,
instructions to edit before checking, and `Decimal.is_finite()` guidance before
ordering comparisons. Although the prompt requested `write`, the native client
completed an allowed `edit` replacing the `assess` body. The 360-second outer
bound ended the run with exit 124 after 360.108 seconds. Its following checker
was not completed. The independent reviewer ran the seven original cases into
a new report, executed the fourteen additional cases declared before the
candidate appeared, checked the scope baseline and reviewed the diff.

Candidate SHA-256:
`dac968f4738761cc85a6b71f0d7265a2d8d1860f122cd22576a9645bc9139fe7`.
The original intent and test hashes are unchanged. The canonical exercise
starter remains unchanged; the candidate belongs to the disposable observation.

The author had prior exposure to worked solutions, and the recovery included
explicit API guidance. No implementation patch or worked answer was supplied
to the client. This is not a blind benchmark. It does not establish a cost,
speed or quality ranking against the unobserved Copilot route.

## Context, resources and accounting limits

Both native source reads returned 9,077 characters for the 671-byte router.
Their `state.metadata.loaded` field names `repo/AGENTS.md`; the full output
contains that integrated guide. The records establish automatic context
inclusion, without assigning it a causal effect on correctness or elapsed time.

The local server used an 8 GiB shared host and eight CPU threads, a 16,384-token
context, one inference slot, q8_0 key/value cache, no prompt-cache allocation
and no context checkpoints. These are the observed settings, not a minimum
requirement. The retained server prefix ends after the final Chapter 1 request
was cancelled, before subsequent MCP/SDD work. Three memory samples show
pressure near the cgroup limit and zero observed OOM kills.

Four completed native steps expose 8,139 uncached input tokens, 543 output
tokens and 9,461 cache-read tokens. Two interrupted requests have no completed
usage receipt. The complete total is therefore unknown. The application cost
field of zero does not measure host allocation, electricity or reviewer effort.
The session totals corroborate completed-step usage and must not be added to it.

## Scope of this extract

`starting_files/` contains the router, integrated guidance, original intent and
the original acceptance source. `STARTING_MANIFEST.json` is the exact manifest
of the complete 1,584-file starting snapshot retained in the author package at
`revision_d7/evidence/native_ch01_01/starting_tree/`. This thin extract is not
that complete snapshot and does not claim to pass the full-snapshot checker
by itself. Its `PORTABLE_MANIFEST.json` binds its actual contents. The completed
full-packet observation and consistency result are copied for reference with
their source scope explicitly stated.

Absolute paths in raw events are historical identities. Generate fresh paths
with the setup helper for a rerun. The old d6 attempt 06 was active and excluded
from CP11; its result remains unknown. D7 success is not a reconstruction of
that missing outcome.

The preparation manifest remains unchanged. The native debug-config probe window
added only a `$schema` declaration to its configuration file. The exact prior
bytes are reconstructed and match the original committed hash; the
[identity note](CONFIGURATION_IDENTITY_NOTE.json) distinguishes that metadata
change from the actual effective behavior and states the observation boundary.
