# Observe the mechanism

The three observations answer different questions: which instruction bytes occur in a recorded client event, which attempted file operations the operating system denies, and which messages a small tool server actually exchanges. None of them is evidence that an autonomous agent followed every instruction.

## Run the portable protocol example

From the unpacked project root with Python 3.10 or later:

```sh
python3 companion/mechanisms/mcp_client.py --output work/mcp
```

Choose a fresh output directory. The command starts the fixed-source server, records nine request/response pairs, and requires no model account or third-party package. It returns exit code 0 only when the checks pass. For the behavioral checks of the published protocol subset:

```sh
python3 companion/mechanisms/verify_profile.py --output work/mcp-profile
```

The profile checks invoke a separate server process, including a valid `tools/call` as the first request. They cover discovery, source identity, returned bytes, rejection paths, required metadata, unsupported versions, and recovery after a rejected request. They do not certify all MCP features.

## Repeat all observations

In a trusted Linux test environment whose setup process can create a different worker identity:

```sh
python3 companion/mechanisms/observations.py --output work/mechanisms
```

The access-control experiment requires a privileged **setup process** with CHOWN, SETUID, SETGID and SETPCAP capabilities. The setup only builds a temporary fixture and starts the shipped probe. It is not a recipe for running a proposed agent patch as root. The worker executes after all capability sets and supplementary groups are cleared, UID/GID are changed to 65534, and `no_new_privs` is enabled.

Without those prerequisites, including on macOS and Windows, the program still records the portable observations but marks the access experiment and overall result `UNSUPPORTED`, exiting with code 2. It does not retry with the worker as owner. Read the retained Linux receipt in `evidence/mechanisms_full_20261102/` when that experiment cannot be repeated locally.

## What the command establishes

| Evidence | Operation | Supported conclusion |
| --- | --- | --- |
| Recorded model run, 22 October 2026 | Re-read the retained OpenCode event and compare the historical `AGENTS.md` body | A client-attached instruction block occurs in the `read` tool result for `routing.py`; the capture does not demonstrate startup injection or compliance. |
| Executed control | Start a worker with a different UID/GID from the protected-file owner | The worker can read the file and write in its own area, but cannot modify the protected file or its relevant directories by the attempted operations. |
| Executed control | Exchange JSON-RPC with the local policy server | The bounded MCP profile completes the recorded reads and distinguishes protocol errors from tool execution errors. No model selects these calls. |

The old CP1.1 permission receipt remains historical. Its initial write and replacement denials did not test the owner's ability to restore permission bits. The new fixture addresses that defect through identity separation, rather than treating `0444` alone as protection.

### Access-control boundary

The protected file is owned by setup UID 0 with mode `0444`. Its `tests/` directory is `0555`; the enclosing fixture is `0755`, also owned by setup. The temporary fixture sits below `/tmp`; the receipt includes its ancestor metadata, including the sticky directory. The worker owns only its `0700` scratch area inside the fixture.

In the same worker process, the probe first reads the actual protected file, then writes and reads a positive-control file. It attempts write, replacement, `chmod` on the file, `chmod` on the protected directory, `chmod` on the fixture parent, and renaming of the protected directory. Each event records the target, expected error class and actual errno. The command also checks owner/mode metadata and the protected file's digest before and after.

This is a file-integrity demonstration on a disposable fixture. It does not constrain network access, CPU use or every file on the host; it is not a general code sandbox. The worker is not trusted to set up its own boundary. A failure to establish the required identity or capability state is a failure of the experiment, not proof of denial.

## Protocol pin and source authority

The main example now pins MCP **2026-07-28**. `PROTOCOL_PIN.json` records the decision; `SOURCES.json` identifies the official pages checked on 2 November 2026. The previous handshake-based captures retain their original **2025-11-25** pin.

Every request carries protocol version and client capabilities in `params._meta`; this client also sends its name and version. `server/discover` advertises the supported revision. Results carry `resultType: complete`; discovery and tool-list results also carry cache freshness and scope. There is no `initialize` or `notifications/initialized` exchange.

`read_policy` accepts one domain argument, `source_id`, with the fixed values `BR-001/v1` and `legacy-note-001`. The schema, request and returned provenance use those same values. The outer JSON-RPC `id` correlates one request and response; it does not identify a policy document.

An unlisted tool name produces a JSON-RPC error. An unknown `source_id`, including a path-shaped string, produces a completed tool result with `isError: true`: the call reached the tool's input boundary, but the value is not permitted. The handler never joins the argument to a filesystem path. A newer returned note remains a `proposal` with owner `unknown`; successful transport does not make it authoritative. `readOnlyHint` remains descriptive, separate from process permissions.

## Evidence files

`RECEIPT.json` records the real execution time, environment, source digests, checks and limits. `agents.historical_event.json` and `agents.historical_output.txt` retain the exact event and output rechecked from the archive. This process does not invoke OpenCode again.

`access.command.json`, `access.stdout.txt`, `access.stderr.txt` and `access.operations.json` retain the setup and probe results. The fixture is removed after observation; its names in the log are historical run paths, not files the reader must recover.

Under `mcp/`, `mcp.stdin.jsonl` and `mcp.stdout.jsonl` contain exact UTF-8 wire lines. `mcp.transcript.json` pairs parsed messages, and `mcp.stderr.txt` contains diagnostics. Stdout contains only JSON-RPC. `excerpts/` contains complete messages rendered as indented JSON and selected-field summaries clearly labelled as projections. Pretty-printing changes whitespace only; the corresponding JSON values remain identical.

The local unsent request-assembly control from CP1.1 is no longer part of the current command or its instruction-delivery claim. The retained client event, the fresh OS fixture and the stdio exchange are separate observations. No new integrated model session or human reader result is implied.
