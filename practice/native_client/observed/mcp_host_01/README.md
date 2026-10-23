# OpenCode MCP observation, 22 October 2026

OpenCode **1.19.3** loaded the unchanged Treasury teaching server through the
official Python MCP SDK **2.3.0**, negotiated **2025-11-25**, discovered
`lookup_policy`, and exposed it as `treasury_lookup_policy`. A local
Qwen3-4B Q4_K_M model selected three real calls. This packet retains the prompt,
effective permissions, native events/export, exact stdio bytes and a declared
serving-process startup probe. No human reader or requirements-owner review was
performed.

Start with [OBSERVATION_SUMMARY.json](OBSERVATION_SUMMARY.json) and compare its
claims with [the native first output](attempt_01/stdout.txt) and the raw
[requests](trace_01/client_to_server.jsonl) and
[responses](trace_01/server_to_client.jsonl).

## Read the failure layers separately

| Observation | Actual result | Attribution |
| --- | --- | --- |
| `BR-001/v2` | Threshold `3000.00`, boundary and synthetic authority returned | Model-selected OpenCode call |
| `BR-999/v1` | `UNKNOWN_POLICY`, domain `ok=false`, envelope `isError=false` | Model-selected OpenCode call |
| Requested `policy_id: []` | Observed argument was the string `"["`; it also returned `UNKNOWN_POLICY` | Native first-output defect; no native list rejection observed |
| Actual `policy_id: []` control | Server returned `isError=true` with a string-type validation error | Separate official SDK `Client(mode="legacy")`, no model or coding host |
| First control startup | Relay could not open its missing trace directory; server was not launched | Control-wrapper defect, preserved before the corrected second control |

The native model's final text falsely described the third call as a schema
rejection. Its argument and the wire bytes contradict that explanation.
[MALFORMED_ARGUMENT_REVIEW.json](MALFORMED_ARGUMENT_REVIEW.json) rejects the claim
and preserves the first output unchanged. The evidence does not establish whether
generation or provider/client parsing caused the malformed attempt to become a
string. A fluent final explanation is not a substitute for inspecting the call.

The separately retained [successful SDK control](legacy_sdk_controls/attempt_02/CONTROL.json)
uses the same `2025-11-25` era and unchanged server. Its raw trace shows the array
reaching the server and the server returning the validation error. It does not
retroactively make the native claim correct. Both control attempts, the failed
script and the corrected executable script remain in `legacy_sdk_controls/`.

## What the permissions and probe establish

The effective native agent disabled file, shell and network tools and allowed
the teaching MCP lookup. The complete ordered permission output also retains
the client's internal tool-output-directory exception. This describes the host's
tool configuration; it does not constrain every operating-system right of a
subprocess.

The actual canonical server interpreter read one explicitly declared, nonsecret
50-byte canary outside the native study directory before MCP initialization.
The read succeeded, with a matching hash. The probe does not establish arbitrary
file access through `lookup_policy`, which accepts literal catalog identifiers.
Post-initialization filesystem restrictions, environment isolation and network
isolation were not tested. The relay and startup instrumentation are not an OS
sandbox. See [PROCESS_BOUNDARY_REVIEW.json](PROCESS_BOUNDARY_REVIEW.json).

The native study file and configured server/relay/probe sources were unchanged.
The catalog hash in the actual lookup result matches the retained catalog bytes.
The captured command ran for 70.56 seconds and exited zero. Those facts do not
validate its incorrect final explanation. Two completed native model steps report
931 input tokens, 352 output tokens and 538 cache-read tokens, 1,821 total under
the client's accounting. Reported local-client charge was zero; total workflow
cost, energy use and human effort were not measured here.

## Reproduce with new evidence paths

Follow `practice/native_client/README.md` in the companion to prepare your
own MCP packet and run the bounded task. Keep its prompt, first output and
wire evidence even when the interpretation is wrong. Do not reuse this packet's
trace directory for another server process.

To repeat only the separate legacy SDK type control, from the companion root
with the pinned MCP environment already installed:

```bash
"$ESA_RUNTIME/mcp_venv/bin/python" -B \
  practice/native_client/observed/mcp_host_01/legacy_sdk_controls/legacy_argument_control.py \
  --server-dir practice/mcp_cli \
  --output "$ESA_RUNTIME/legacy_argument_control_new"
```

Choose an unused output path. This command makes no model request. The simpler
standard-library CLI and the earlier modern SDK comparison remain separate
exercises; this packet makes no paired performance claim.

`NATIVE_OBSERVATION.json` and `CONFIGURATION_MANIFEST.json` preserve the initial
unfilled preparation state. [OBSERVED_NATIVE.json](OBSERVED_NATIVE.json) is the
distinct completed evidence record. Its structural check establishes file/hash
consistency only; action acceptance requires review against the original criteria.
