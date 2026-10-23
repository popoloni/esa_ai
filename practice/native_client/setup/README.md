# Retained setup records

[runtime_d7/](runtime_d7/) records the fresh 22 October 2026 reconstruction of
the pinned OpenCode 1.19.3, llama.cpp b11799 and Qwen3-4B Q4_K_M stack. Its index
binds public download receipts, installed identities, package lock and setup
failures. The original `START.json` is a start event; it is preserved rather
than rewritten as a finish event. Installed version output, checked artifact
hashes and the Chapter 1 server lifecycle establish the resulting availability.

The executable runtime, model and dependency trees are not included. Use the
[parent guide](../README.md) to reconstruct them in a new directory, or inspect
[the native Chapter 1 evidence](../observed/ch01_01/README.md) without installing
the model. Historical d6 task records remain distinct in that packet's
`historical_d6/` directory. Their then-active excluded attempt has no known
outcome.

[runtime_d7/diagnosis/](runtime_d7/diagnosis/README.md) is a separate, attributed
packet explaining the pinned client's response-header timeout, automatic title
request and configuration-schema insertion. It retains the relevant upstream
source, license, log excerpts and read-only resource observations. Its own
manifest supplements the original setup index without changing that index's
recorded scope.

Closed server lifecycles have their own small packets:

| Packet | Recorded configuration and scope |
| --- | --- |
| [Original shared server](runtime_d7/llama_server_01/README.md) | 16,384-token context and q8_0 K/V; Chapter 1, MCP and the first SDD attempt, followed by the retained shutdown. |
| [Corrected-context server](runtime_d7/llama_server_02/README.md) | 24,576-token context and q4_0 K/V; the first corrected SDD response, resource samples and shutdown. |
| [Final guided-continuation server](runtime_d7/llama_server_03/README.md) | Same 24,576/q4_0 settings; exact input read, client timeout, retained active-request sample and forced server cleanup. |

The server packets record service intervals and their actual shutdown outcomes.
Server01 and server02 exited cleanly; server03 required a recorded forced stop.
Neither outcome establishes client task completion. Their wall or CPU totals
are not a complete cost account for an individual task.

## Stopping a future local server

The current `run_local_model.py` accepts `--shutdown-grace-seconds` (default
30 seconds). The first SIGTERM or SIGINT to the launcher starts one monotonic
grace interval and requests SIGTERM for its direct child. Repeated signals do
not restart that interval. If the same child is still running when the interval
expires, the launcher requests SIGKILL for that child and records the actual
events and exit. Polling, scheduling and I/O can add delay; this is not a hard
real-time deadline or a process-containment claim.

This correction follows the retained server03 cleanup. Its original launcher
and observed manual escalation remain historical evidence; they are not
rewritten as a run of the corrected helper. No additional model observation is
implied by the source correction.

[The shutdown guard](runtime_d7/shutdown_guard/README.md) preserves the old
launcher, the corrected source identity, the failed PID-view controller
preparation and the successful inert subprocess checks. It explains the
future bounded stop behavior separately from the actual server03 outcome.

[MCP dependency receipts](mcp_d7/) and
[native host observations](../observed/mcp_host_01/README.md) use their own dated
records. The host packet distinguishes actual model-selected calls, the
reviewed first explanation, a separate SDK validation control and the measured
startup process boundary.

## d8 native Spec Kit runtime

[The d8 runtime packet](runtime_d8/README.md) retains the later 24,576-token
f16 server, exact launcher, pinned source diagnosis, startup/resource checks
and closed lifecycle. It distinguishes observed client response limits from
unproven server cap enforcement, preserves the earlier failed attempts and
links the native specification response and its separate persistence defect.
Its own manifest supplements the historical d7 setup without changing it.
