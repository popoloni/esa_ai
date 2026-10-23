# Local runtime used for the d8 native Spec Kit observation

This packet preserves the actual local server configuration, resource checks,
request timings and closed lifecycle used for the 22 October 2026 d8 journey.
The [native SDD route](../../../sdd/NATIVE_ROUTE_D8.md) explains the installed
framework command, complete inputs, failed attempts, guided continuations and
the useful final response. Its [observation packet](../../../sdd/observed_native_20261022_d8/)
contains the client evidence and editorial reader copy.

The runtime observations do not establish successful persistence of the
substantive specification or human acceptance. The native final response preserved the specification and stopped
with the three owner questions unanswered. The saved project file remained an
incomplete input echo, and the response's three-artifact completion claim was
false. The [independent review](review/R08_ATTEMPT_04_INDEPENDENT_REVIEW.json)
assesses the original bounded tutorial criteria with those defects disclosed.

## Start with these records

| Record | What it establishes |
| --- | --- |
| [Runtime summary](RUNTIME_SUMMARY.json) | Selected actual settings, request measurements, resource limits and terminal identities, with source bindings. |
| [Observed launcher](preparation/run_local_model_d8.py) | Exact source used for the d8 server; its SHA-256 is `c9bc0eb8e64725c7b1ba92687cdfcf4ffd87c5648c0c3abb2e08d4854c3c5b4f`. |
| [Startup review](observed/startup_04/REVIEW.json) | Actual health, context, backend and conservative memory assessment before the later native attempts. |
| [Server start](observed/lifecycle_04/START.json) and [finish](observed/lifecycle_04/FINISH.json) | Exact arguments and the service interval; the server exited 0 after the recorded stop. |
| [Actual attempt04 runtime](observed/attempt04_runtime/OBSERVATION_SUMMARY.json) | Two completed requests, native usage attribution, sparse memory samples and the final pre-stop idle state. |
| [Candidate03 configuration](observed/client_candidate03/OPENCODE_CONFIG_03.json) and [attempt04 configuration](observed/client_attempt04/OPENCODE_CONFIG_04.json) | Actual client settings, including the later change from 3,072 to 1,536 configured response tokens. |
| [Source map](SOURCE_MAP.json) and [portable manifest](PORTABLE_MANIFEST.json) | Exact-copy provenance and the identities of every file in this packet. |

Copied records retain their original absolute paths and contemporaneous claims.
Those paths identify the observed workspace; they are not runnable paths on a
new computer. `SOURCE_MAP.json` maps each copied author-side record to its
portable location. The earlier d8 summaries remain dated assessments; the
later useful response does not repair their failed outputs.

## Actual server settings

The installed stack was OpenCode 1.19.3, Spec Kit 1.2.2, llama.cpp b11799
(commit `0756e83fc`) and Qwen3-4B Q4_K_M. The server executable and weights were
reused from the [retained d7 reconstruction](../README.md). Real model weights,
executables and installed dependency trees are not distributed in this packet.
The small model-shaped file inside the preparation's controlled probe is
plain-text inert test data; that probe performed no inference.

The observed server used one 24,576-token slot, f16 key and value caches, flash
attention, eight generation threads and eight prompt threads, batch 256 and
microbatch 128. It loaded `libggml-cpu-zen4.so` in an environment with an
eight-CPU quota and an 8 GiB cgroup memory limit. GPU layers, reasoning,
context shifting, weight repacking and startup warmup were disabled. The
service listened only on `127.0.0.1:18080`; built-in server agent tools, MCP
proxy and web interface were disabled. These options are not an operating-system
sandbox or a claim of complete network isolation for the separate client.

The original [preparation plan](preparation/RESOURCE_PLAN.json) proposed
22,528 context tokens. The measured full input and reserves did not fit that
candidate, so the actual later lifecycle used **24,576**, explicitly on the
command line. The immutable launcher still has a 22,528 default. Always pass
the intended context explicitly. The original preparation README also calls
the client `steps=12` a cap; pinned client behavior and the actual episode show
that it is a last-step instruction, not a mechanical twelve-request stop.
Neither historical wording is silently corrected inside the preserved record.

## What bounded the actual work

| Boundary | Candidate03 native invocation | Compact attempt04 continuation |
| --- | --- | --- |
| Declared client context | 24,576 tokens | 24,576 tokens |
| Configured response output | 3,072 tokens | 1,536 tokens |
| Provider overall and header deadlines | 1,500 seconds each | 1,500 seconds each |
| Capture's prospective outer deadline | 5,400 seconds | 2,400 seconds |
| Native `steps` value | 12; last-step guidance | 12; last-step guidance |
| Agent temperature intent | 0.2, with model temperature capability enabled | Same |
| Actual observed sampler temperature | 0.2 | 0.2 |

The compact request's 650-token content target was prose guidance. It was not
an enforced token limit. The server launcher requested `--n-predict 3072`, but
the actual `/props` response reported `max_tokens=-1` and `n_predict=-1`.
The logs expose no request-specific maximum-output field. Both completed
attempt04 responses were below 1,536 tokens; this alone does not prove that
the client or server enforced the cap. Keep the configured client limit,
observed response length and independent server enforcement as separate claims.

The launcher had a finite 7,200-second service lifetime and a 30-second
shutdown grace measured from the first stop request. Repeated signals do not
reset that grace. Its escalation target is only its own still-running direct
child. Scheduling and I/O can add delay. The service lifetime includes startup
and preparation time, so check the remaining interval before starting a client
with a long outer deadline. The observed service was restarted before the later
journey to preserve that prospective budget; no active deadline was extended.

## Memory and timing evidence

The startup assessment reserved cgroup anonymous memory, all kernel memory,
shared memory and the full size of unique mapped regular files. This deliberately
reserves all model pages even when not resident. It is an estimate, not the
kernel's exact available-memory value. Other file cache was treated as
reclaimable. Startup04 estimated 1,296,768,616 bytes of headroom against its
768 MiB startup gate. That gate was not an automatic runtime abort threshold.

Seven sparse attempt04 samples, including a checkpoint pause in sampling,
recorded a minimum conservative headroom of 665,919,080 bytes and no new OOM
or OOM-kill event. The samples do not establish a continuous peak or guarantee
that another machine or larger history will fit.

| Actual attempt04 request | Prompt tokens | New prompt tokens evaluated | Prompt evaluation | Generated tokens | Generation time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Server task 3263 | 18,599 | 255 | 17.422 s | 553 | 296.037 s |
| Server task 3818 | 19,169 | 574 | 68.137 s | 1,393 | 769.740 s |

These are request measurements from a warm, continuing native session. They
are not cold-start benchmarks or a controlled comparison of cache formats.
Pinned [CPU source](preparation/upstream/llama.cpp-0756e83fc/ops.cpp) supports
the diagnosis that compatible f16 K/V can use an optimized attention path
unavailable to the prior quantized-cache choice. Input packaging, batch sizes,
cache state and other settings also changed. The packet makes no causal
speedup estimate.

The native capture ended normally at 12:05:40.713363 UTC. Its runtime summary
was frozen while the server remained idle and running. The later
[stop decision](observed/SERVER04_STOP_DECISION.json),
[shutdown record](observed/lifecycle_04/SHUTDOWN.json), finish receipt and
[host observation](observed/SERVER04_TERMINAL_HOST_OBSERVATION.json) separately
establish exit 0 at 12:14:56.098849 UTC with both owned PIDs absent. There was
no forced escalation in this lifecycle. A tool's unavailable execution-session
poll is not used as proof of process termination.

Native completed usage and backend counters retain their own units and
attribution. Reported local cost fields of zero do not establish zero monetary
or human cost. Service wall/CPU totals include multiple attempts; they are not
a whole-workflow cost account. Interrupted earlier requests retain missing
native usage rather than borrowing the final response's counts.

## Recipe for a new local attempt

Use a fresh runtime and evidence location and follow the pinned reconstruction
instructions in the [native client guide](../../README.md). From the companion
root, the following illustrates the **observed server settings**, with paths
chosen for the new machine:

```sh
ESA_RUNTIME_ROOT=/absolute/path/to/pinned-runtime
ESA_SERVER_EVIDENCE=/absolute/path/to/new-server-evidence
python practice/native_client/setup/runtime_d8/preparation/run_local_model_d8.py \
  --runtime-root "$ESA_RUNTIME_ROOT" \
  --evidence "$ESA_SERVER_EVIDENCE" \
  --ctx-size 24576 \
  --cache-type-k f16 --cache-type-v f16 \
  --threads 8 --batch-size 256 --ubatch-size 128 \
  --shutdown-grace-seconds 30 --max-runtime-seconds 7200 \
  --print-plan
```

`--print-plan` starts no child. Inspect the planned arguments and pinned local
file identities. Remove that final flag to start the service. Confirm the new
health and `/props` responses, actual backend, context, CPU allocation, memory
headroom and OOM counters before inference. Recalculate the complete native
input plus current-response and cumulative-history reserves. A successful
health response does not establish those later gates.

Use the [d8 SDD route and configuration helper](../../../sdd/NATIVE_ROUTE_D8.md)
for a new isolated project and client state. The complete installed command
and source packet must remain intact. The source attachment was user-selected
native input ingestion; it was not a model-selected source read. Model reads
were subsequently limited to generated outputs to prevent duplicating that
full packet in history. The observed configurations contain old absolute paths
and a session ID; regenerate them rather than executing those copied task
records as a new run. There is no promise of identical model output or correct
persistence from repeating the settings.

Stop a new service by verifying its fresh `START.json` and the actual process
identity, then sending SIGTERM to that launcher's PID. Use the resulting
SHUTDOWN/FINISH records and an appropriate process check to establish the
outcome. Do not reuse the historical PIDs in this packet or terminate unrelated
processes.

## Attribution and retained history

`preparation/upstream/llama.cpp-0756e83fc/` and
`preparation/upstream/opencode-v1.19.3/` retain exact pinned primary-source files
with their MIT licenses. [SOURCE_RETRIEVAL.json](preparation/SOURCE_RETRIEVAL.json)
binds the official source URLs and copied-license identities, including earlier
lookup failures. [The launcher diff](preparation/LAUNCHER_DIFF.patch) preserves
its change from the retained corrected d7 launcher; the inert lifetime test
and fixtures remain in the preparation packet.

The [d7 setup and failures](../runtime_d7/) remain a separate historical
record. The three earlier d8 monitor summaries here retain the duplicated-input
context failure, template-only result and timed-out generation. Their full
author-side evidence remains in the revision archive; the native SDD packet
preserves the associated client failures and original outputs.
