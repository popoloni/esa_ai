# One read-only task through MCP and a CLI

**Task:** retrieve the synthetic `BR-001/v1` policy, including its threshold,
boundary, authority and source identity. Both paths call `policy_lookup.lookup`.
The same exercise also queries v2 and a path-like unknown identifier.

## Predict and run the simple path

From `companion/`, predict which queue receives an amount equal to EUR 5,000,
then run the standard-library CLI:

```bash
python3 practice/mcp_cli/policy_cli.py lookup BR-001/v1
python3 practice/mcp_cli/policy_cli.py lookup ../../outside.json
```

The first returns `ok=true`, threshold `5000.00` and the inherited boundary.
The second returns `UNKNOWN_POLICY` and exit 2. The argument selects from two
literal identifiers. It is never joined to a filesystem path.

## Run the optional official SDK path

This example pins the official `mcp` Python SDK at **2.3.0**. The complete
observed dependency set is in `requirements.lock`; it is a version lock, not a
wheel-hash attestation. Install it in a separate virtual environment. From
`companion/` on a POSIX shell:

```bash
python3 -m venv ../mcp_example_env
../mcp_example_env/bin/python -m pip install -r practice/mcp_cli/requirements.lock
../mcp_example_env/bin/python -B practice/mcp_cli/compare.py --output ../mcp_run_01
```

Use a new output directory on every run. Installation requires access to the
public package registry; the observed policy exercise itself configures a local
stdio subprocess and no HTTP endpoint. Windows virtual environments use a
different executable path and are not validated by this receipt.

`policy_server.py` registers one typed tool, `lookup_policy(policy_id: str)`.
The SDK publishes its JSON schema. `compare.py` uses the SDK Client, captures
modern server discovery and per-request version metadata, lists the tool, makes three calls, and sends one
schema-invalid list argument. `wire_proxy.py` is an exercise-only relay that
retains the exact request/response lines. No model chooses these calls.

## Read the two protocol eras correctly

Chapter 2 keeps a small handwritten fixture so that a reader can see dispatch
and errors without installing dependencies. It implements **2025-11-25**, the
initialization-based protocol era. This SDK exercise records **2026-07-28**,
which removed that handshake. These are intentionally different examples:

| Path | Opening exchange | Version and capabilities | What the evidence establishes |
| --- | --- | --- | --- |
| `reader_side/mcp/contract_server.py` | `initialize`, then `notifications/initialized` | The initialization request/result carry the legacy version and capabilities | A narrow handwritten teaching fixture and its local tests |
| This SDK 2.3.0 observation | `server/discover`, followed by `tools/list` and `tools/call` | Every request carries `io.modelcontextprotocol/protocolVersion` and `io.modelcontextprotocol/clientCapabilities` in `params._meta` | Actual SDK processes exchanged the retained modern messages |
| OpenCode 1.19.3, observed 22 October 2026 | `initialize`, then `notifications/initialized` and `tools/list` | Negotiated `2025-11-25` with the same SDK 2.3.0 server | Actual host discovery and model-selected calls; see the separate [native packet](../native_client/observed/mcp_host_01/README.md) |

In the modern SDK comparison, the first retained request is `server/discover`. Its result advertises
`supportedVersions: ["2026-07-28"]`, capabilities and server identity. Each of
the six requests then identifies the same protocol version in `_meta`; the
trace also includes `clientInfo`. There is no `initialize` request and no
`notifications/initialized` notification in this run. Modern clients may use
discovery for up-front version selection; it is not a mandatory initialization
handshake. Dual-era clients can use a transport-specific compatibility probe.
Do not assume every modern client interoperates with the legacy fixture.

The installed Python **distribution** version is `mcp==2.3.0`. The SDK's
advertised **wire identity** here is `{"name":"mcp","version":"0.1.0"}`.
Those fields identify different things; the wire value is not evidence that
the installed package was version 0.1.0.

Inspect the retained bytes with the standard library alone:

```bash
python3 practice/mcp_cli/inspect_trace.py \
  practice/mcp_cli/observed/attempt_02_local_stdio_pass
```

The check binds the three source files by hash, pairs response IDs, checks the
recorded request sequence and required modern metadata, and reports the two
version identities separately. It validates this exercise's trace shape, not
all MCP behavior or a new connection. The [2026-07-28 change log](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
and [lifecycle and compatibility rules](https://modelcontextprotocol.io/specification/2026-07-28/basic/lifecycle)
were checked on 21 October 2026.

## Inspect the observation

`observed/attempt_02_local_stdio_pass/COMPARISON.json` records Python 3.12.14,
SDK 2.3.0, protocol `2026-07-28`, the three equal domain results and the rejected
schema-invalid call. It binds the catalog before/after and every evidence file.
The raw stream records actual modern discovery and requests, not a
hand-authored transcript or a legacy initialization exchange.

| Observed item | Serialized UTF-8 bytes | What the number means |
| --- | ---: | --- |
| MCP tool-list result | 552 | The schema/description JSON in this one run |
| Successful MCP call result | 1,223 | SDK result JSON, including text and structured content |
| Successful CLI stdout | 472 | CLI JSON plus its newline |
| Unknown-ID MCP result | 483 | Domain refusal inside the SDK result envelope |
| Unknown-ID CLI stdout | 122 | The equivalent refusal in CLI output |

These counts use deliberately disclosed serialization rules and unequal
envelopes. A host decides how much tool metadata and content it inserts into
model context. These bytes are not token counts, invoices, latency rankings or
proof that either interface is cheaper. Single-run durations include different
startup costs and remain in the receipt only as local observations.

The first attempt, `observed/attempt_01_restricted_timeout/`, did not complete
discovery in the restricted process environment. Its empty server-response
stream, timeout and traceback are retained. A direct SDK diagnostic also timed
out there; an in-memory SDK call succeeded. Before the successful run, the
server's return annotation also changed from `dict` to `dict[str, Any]` to
publish structured output. The two retained attempts therefore differ in both
execution environment and source revision. Running the revised local stdio
comparison outside the restricted process sandbox succeeded. This is a usable
observed setup, not a controlled same-source diagnosis of the timeout or proof
of a specific upstream SDK defect. The source hashes disclose the difference.
Do not silently retry in a wider-permission environment without checking the
task and the permissions you are granting.

## Make the interface decision

Choose the CLI when a person or script knows this one fixed command and needs
its JSON. Choose an MCP integration when a compatible host needs tool discovery,
argument schema and protocol result handling. The domain behavior is shared;
the additional interface must earn its maintenance cost in the actual workflow.

The API accepts no file path, exposes no write operation and supplies no
credentials. The source catalog hash is unchanged in the observed run. The SDK
starts the server with its default environment allow-list plus the explicit
bytecode flag, rather than an application credential. These are application
and setup facts. The process still has its operating-system rights. No separate
network-egress audit, OS sandbox certification or human acceptance is recorded
here. The separate OpenCode observation below records actual host interoperability
within its declared scope. Stdio alone proves no isolation boundary.

## Source and maintenance

The official SDK's [release page](https://pypi.org/project/mcp/2.3.0/),
[client transports](https://py.sdk.modelcontextprotocol.io/client/transports/),
[server execution](https://py.sdk.modelcontextprotocol.io/run/) and
[structured output](https://py.sdk.modelcontextprotocol.io/servers/structured-output/)
were checked on 20 October 2026. The SDK main branch can evolve beyond the pin.
Upgrade in a fresh environment, retain old and new receipts and reread the
schemas before changing this version. The compact educational server in
Chapter 2's core fixture remains a separate teaching implementation.

## Inspect the named-host observation

[The OpenCode packet](../native_client/observed/mcp_host_01/README.md) retains
actual host configuration, discovery, model-selected lookup results and a
declared startup read by the serving interpreter. The first output also contains
a real error: the model claimed a list argument was rejected by the schema,
but both its recorded tool input and the wire carried the string `"["`. That
string produced `UNKNOWN_POLICY`; it was a domain refusal. The review rejects
the unsupported explanation without rewriting the first output.

A separate actual SDK control sends `[]` over the same legacy protocol and
retains the server's type-validation error. Its first relay-startup failure and
corrected rerun are both preserved. These controls are explicitly attributed
to the SDK; they do not stand in for a native host argument rejection that was
never observed. The successful serving-process canary read establishes one
specific startup capability, not OS containment or arbitrary model file access.

Follow [the native collection route](../../validation/NATIVE_HOST_COLLECTION.md)
to collect a new observation. It separates missing client, failed process
startup, absent discovery, argument rejection, domain refusal and actual process
boundary observations. The standard-library `diagnose_trace.py` can inspect both
retained attempts now; it launches no SDK or model. The named-host collection
above adds its own native evidence; the earlier modern SDK/CLI comparison
remains unchanged.
