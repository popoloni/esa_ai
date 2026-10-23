# d8 native server preparation

This packet prepares a separate, bounded local-server configuration for the newly authorized R08 native Spec Kit journey. The d7 source, launcher and failed observations are preserved. **No model request was made while preparing this packet.** Root starts the server only after the checkpoint and then checks health, memory and the exact native input token budget before permitting generation.

## Exact candidate

Use the argv array in `LAUNCH_COMMAND.json`; `PLANNED_LAUNCH.stdout.json` expands the resulting server arguments without starting a child. The candidate reuses pinned llama.cpp b11799 / commit0756e83fc and the already installed Qwen3-4B Q4_K_M weights. It uses22,528 context tokens, f16 K and V, one slot, eight CPU threads, logical batch256 and physical batch128. Weight repacking, startup warmup, reasoning and context shifting are disabled. No server-side agent, MCP proxy or web interface is enabled.

`run_local_model_d8.py` derives from the exact retained `D7_CORRECTED_LAUNCHER_BASE.py`; `LAUNCHER_DIFF.patch` discloses the changes. The direct-child shutdown guard remains: the first stop request sets a monotonic30-second grace, repeated signals do not reset it, and only that still-running child may be killed. A separate7,200-second maximum server lifetime uses the same bounded stop path. This maximum includes preparation time; the native client has its own fixed5,400-second outer ceiling,1,500-second provider/header deadlines,3,072-token per-response maximum and12-step cap. These are ceilings, not expected completion time or promises of acceptance.

## Why this candidate

The retained d7 server log attributes the prior delay to prompt processing:6,964 initial tokens required728.010seconds before55 output tokens took18.109seconds. After the real client read the complete packet, the next request reused6,960 cached tokens but still spent1,045.01seconds processing4,096 additional input tokens before the fixed outer stop. Thinking had already been disabled. The8-thread setting matched the observed8-CPU quota.

Pinned `ops.cpp` selects its tiled CPU attention path only for compatible f32/f16 K and V; q4_0/q8_0 do not take that branch. This is a source-backed performance hypothesis, **not a measured f16 speedup**. The exact installed archive includes optimized CPU libraries; prior logs do not prove a generic backend was selected. The new startup must retain the actual loaded backend and resource records.

Pinned `arg.cpp`, `common.cpp` and `llama-model.cpp` show that `--no-repack` omits optional extra CPU weight buffers while retaining the ordinary CPU fallback. `BINARY_HELP.json` and its complete stdout/stderr establish support in the actual installed executable. The memory saving and throughput effect remain unmeasured. The model weights and semantic requirements are unchanged; floating-point/kernel-path results are not asserted to be bit-identical.

## Resource and input gates

`RESOURCE_PLAN.json` gives the raw cache formula, estimates, source locations and required gates. Raw f16 K+V at22,528 consumes3,321,888,768bytes (3.09375GiB); that is only one part of memory use. The old peak RSS with a smaller q4 cache cannot establish safety for this candidate. Root must retain actual RSS, cgroup anon/kernel/file/cache fields and OOM counters, and require conservative working headroom for the native client and growth. No host-wide cache purge is used.

The unchanged installed Spec Kit command receives the complete line-safe fixed source packet through native absolute `@file` expansion. Pinned OpenCode1.19.3 ignores CLI `--file` in its `--command` branch, so that route is not used. This is user-selected native attachment ingestion, not a model-selected source-read tool call. Sibling preflight verifies complete9-JSON-value and4-exact-body ingestion with no truncation. The actual combined command, attachment, system/tool envelope, output reserve and cumulative history must fit the measured server context before inference.

## Evidence and attribution

`RUNTIME_PREFLIGHT_BEFORE_START.json` retains actual binary/model hashes and read-only resource observations. `SOURCE_RETRIEVAL.json` identifies every copied or downloaded pinned primary source and retains earlier lookup failures. Both upstream directories include their corresponding MIT licenses. Source filenames retain pinned versions rather than implying current upstream behavior.

A successful startup or HTTP health result does not close R08. Actual named-client tool calls, generated framework artifacts, independent acceptance checks and any clarification dialogue must be recorded separately. d7 remains partial, and all new outcomes belong to d8.

## Controlled launcher check

`CONTROLLED_PROBE.json` records an actual inert Python-child test of the new automatic lifetime stop. The fake executable ignores SIGTERM, so the launcher reaches its monotonic0.4-second grace and kills only that child after the0.8-second lifetime; actual elapsed time was1.253seconds, all8checks passed. This probe used a plain-text dummy model file and performed no llama execution, networking or inference. It validates the lifecycle guard, not model memory or performance. The fixture/controller and full START/SHUTDOWN/FINISH/stdout/stderr records are retained.
