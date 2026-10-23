# OpenCode 1.19.3 behavior diagnosis

This packet explains three behaviors encountered during the native observations
on 22 October 2026. It combines retained client log excerpts with the exact
upstream source files for release `v1.19.3`. The investigation was read-only:
it did not change the active server, an observed configuration, or an observed
session. Corrected recipes apply to newly prepared attempts.

## What the pinned source establishes

| Behavior | Source and observed evidence | Consequence for a future bounded attempt |
| --- | --- | --- |
| Response-header timeout is separate from the overall timeout. | `provider.ts` defines a default `headerTimeout` of 300,000 milliseconds independently of `timeout`. The native SDD log records `ProviderHeaderTimeoutError` after 300,000 milliseconds while its configured overall timeout was 600,000. | Specify a finite `headerTimeout` as well as a finite overall `timeout`. Preserve both settings in the generated configuration. |
| A new session can start a separate title-generation request. | `session_prompt.ts` starts title generation for a default-title session with one real user message. `cli_run.ts` passes an explicit `--title` into session creation. The retained native log directly records `small=true agent=title` before the main SDD agent. | Give a bounded run an explicit, nondefault title so this title-generation path returns before making a model request. |
| Loading a configuration without `$schema` can amend that file. | `config.ts` inserts `https://opencode.ai/config.json` and writes the amended text back when the loaded configuration has a file path and no schema. The native repair and MCP records separately reconcile their preparation hashes with the actual files. | Include that exact schema value when creating future configurations. Keep the original preparation manifest and disclose any already observed change. |

[`DIAGNOSIS.json`](DIAGNOSIS.json) contains the source hashes, code locations,
dated log excerpts, findings, and their limits. The automatic title request is
directly observed in the client log; a one-to-one mapping between that request
and a particular server task was not captured at the HTTP-request level.
The later server task had a larger prompt, so these records do not establish
a same-prompt retry-cache benefit. Ordinary completed-step usage does not
establish a complete token or monetary account for title generation or aborted
requests.

## The retained resource check

[`POST_SDD_RESOURCE_SNAPSHOT.json`](POST_SDD_RESOURCE_SNAPSHOT.json) records the
process and cgroup state after the first SDD client stopped. The configured
eight CPU threads match an eight-CPU quota (`cpu.max` of `800000 100000`);
this check found no thread/quota mismatch. The cgroup had an 8 GiB memory
limit, about 7.35 GiB in use, and zero recorded OOM or OOM-kill events. Those
counters and memory values are observations at a particular boundary, not a
controlled explanation of the earlier latency.

[`POST_SDD_SERVER_PROPERTIES.json`](POST_SDD_SERVER_PROPERTIES.json) retains
the subsequent successful read-only `/props` and `/metrics` responses. They
show a 16,384-token context, one slot, and zero processing or deferred requests.
The first restricted loopback read failed; its actual error remains in the
resource snapshot, and the later authorized read is a separate record. Exact
KV-cache allocation was not exposed by these records. Neither snapshot is a
hardware minimum, a performance benchmark, or evidence that a longer retry
would finish the workflow.

## Source identity and reuse

The four TypeScript files are retained byte-for-byte from the public
[OpenCode `v1.19.3` source](https://github.com/anomalyco/opencode/tree/v1.19.3).
[`SOURCE_DOWNLOADS.json`](SOURCE_DOWNLOADS.json) and
[`TITLE_SOURCE_DOWNLOADS.json`](TITLE_SOURCE_DOWNLOADS.json) retain the exact
URLs, retrieval results, sizes and SHA-256 hashes, including the unsuccessful
`session/index.ts` lookup. The explanation and local observations are separate
author files.

The upstream MIT notice is retained in
[`UPSTREAM_LICENSE.txt`](UPSTREAM_LICENSE.txt). It was copied byte-for-byte
from the installed `opencode-ai` package after its version `1.19.3` and MIT
license metadata were checked. [`UPSTREAM_ATTRIBUTION.json`](UPSTREAM_ATTRIBUTION.json)
records that origin and the notice's hash. No source file was changed during
this diagnosis.

The portable copy has its own `PORTABLE_MANIFEST.json`. The original runtime
setup index and the historical native observation manifests keep their
original scopes and identities.
