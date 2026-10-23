# Collect one named coding-client journey

This route prepares an observation of a client that you actually have installed
and are authorized to use. The supplied example remains **NOT_RUN** for VS Code
with GitHub Copilot and Claude Code. A local command rehearsal, an SDK transcript,
and this packet checker do not change that status.

One observed primary route is enough for the book's R06 tutorial criterion.
The contrasting route can remain explicitly unobserved, with one documented
workflow difference and no paired performance claim. Native skills or delegated
workers are useful only when the bounded task needs them; they are not an extra
mandatory condition for R06. Record a claimed native capability if you use one.

## 1. Establish what is available

From the companion directory:

```bash
python3 practice/agent_workflow/client_preflight.py --output ../native_preflight_01.json
```

Read the version command's exit status, not just the PATH result. A launcher can
exist while the product is absent. For VS Code, also retain the actual Copilot
extension version and the interface's exposed model identity. Authentication
status comes from your authorized client interaction; this preflight never reads
credentials or tests an account. If no supported client can run, stop the native
route and retain the preflight. The offline activities below remain useful.

Confirm the current client help, effective permissions and dated adapter notes
before using it. Keep the startup configuration you actually loaded. Remove any
secret values before retaining logs, and describe the redaction without changing
the meaning of a request or outcome.

## 2. Preserve a fresh starting tree

Create one study copy and then its evidence directory. Do not prepare the same
copy twice or substitute a previously repaired candidate.

```bash
python3 reader_start.py new 1 --destination ../native_work_01
python3 validation/observe_native.py prepare \
  --source ../native_work_01 --output ../native_evidence_01 --actions R06 R07
```

Preparation retains the initial file bytes in `starting_tree/` and their hashes
in `STARTING_MANIFEST.json`. It excludes Git internals, virtual environments,
package caches and bytecode using the existing command recorder's inventory
rules. This route refuses symlinks and a source that changes during copying.
It does not make a copy of undisclosed external files or a sandbox.

The new `NATIVE_OBSERVATION.json` is deliberately incomplete. Set the actual
client name/version and state whether the model identity was exposed. Unavailable
model details stay null with `model_identity_availability: NOT_EXPOSED`; do not
invent a release. Describe prior access to answers, including the worked solution
files delivered with the lab. A prompt asking the agent not to read them is not
an access boundary or a blind-evaluation design.

## 3. Retain the first failure, task and first output

Follow `reader_start.py show 1` in the new study copy. Keep the initial seven-case
failure before allowing an edit. Give the client the current intent, the sole
editable file `repo/src/treasury/routing.py`, and a stop at human review. Capture
the prompt exactly. The first generated response must be retained even if it is
wrong or cannot execute. Keep a separate attempt after any correction.

For a command you are authorized to run, create a task JSON with literal argv,
absolute `cwd` and `inventory_root`, and exact `allowed_changed_files`. For
example, a version check has no permitted source changes:

```json
{
  "origin": "native_client_version_probe",
  "tool": "the installed client name",
  "tool_version": null,
  "model": null,
  "argv": ["the actual executable", "--version"],
  "cwd": "/absolute/path/native_work_01",
  "inventory_root": "/absolute/path/native_work_01",
  "allowed_changed_files": [],
  "timeout_seconds": 30
}
```

Replace those values with the paths and invocation established by your client.
Then run:

```bash
python3 validation/observe_native.py capture \
  --spec ../native_version_task.json --output ../native_evidence_01/version_01
```

The shared recorder retains the task, literal command, stdout, stderr, actual
exit status and before/after inventories. An unsuccessful command returns a
nonzero recorder status and remains available for diagnosis. It never retries
with wider permissions. For an editor interaction, export its real native log
and retain the UI actions separately; do not represent a shell wrapper as having
captured an editor's model or internal tool choices.

Finish with a source diff and independent owner-side checks. Record the reviewer
as human or assistant. The current checker's result and a model's agreement do
not grant human acceptance.

## 4. Observe MCP at the layer that failed

Use `practice/mcp_cli/policy_server.py` and its pinned optional SDK environment.
Keep the actual host configuration and server version. Do not replace the
read-only server with a more powerful probe just to obtain a green result.

| Layer | Evidence to retain | Interpretation |
| --- | --- | --- |
| Client availability | Version command, exit status, installed extension identity | A missing executable or broken launcher precedes any host session. |
| Server startup | Exact interpreter/argv, stderr, process exit or timeout | A failed process start differs from an unanswered protocol request. |
| Opening exchange and discovery | Raw protocol messages and the host's tool list | Legacy `2025-11-25` uses initialization; modern `2026-07-28` uses discovery/version metadata. Record the era actually used. |
| Model tool selection | Native tool invocation and the prompt that elicited it | Tool publication alone does not show that the model selected it. |
| Arguments | The real schema-invalid request and rejection | A list supplied to a string parameter is an argument failure. |
| Domain result | Valid lookup and unknown-policy request/result | A well-formed unknown ID is a domain refusal, distinct from a malformed request. |
| Process boundary | Effective host/OS settings and one declared non-secret canary probe | Read-only tool shape does not establish process filesystem, environment or network isolation. |

Use a disposable non-secret canary for a permitted boundary probe. Record which
process performed it, the declared expectation, result and source identity.
A sibling Python process reading the canary tests that process, not the host's
MCP sandbox. Leave other boundaries `NOT_TESTED`; a single successful refusal
cannot certify an entire isolation mechanism. Keep permission changes and failed
attempts instead of silently broadening the environment.

The retained SDK traces can be diagnosed offline without a new SDK install:

```bash
python3 practice/mcp_cli/diagnose_trace.py \
  practice/mcp_cli/observed/attempt_01_restricted_timeout
python3 practice/mcp_cli/diagnose_trace.py \
  practice/mcp_cli/observed/attempt_02_local_stdio_pass
```

The first has no opening response and cannot by itself identify a startup or
transport cause. The second distinguishes successful results, the unknown-policy
refusal and the invalid-argument rejection. Both commands inspect old evidence;
neither launches a named host or establishes a new model observation.

## 5. Bind evidence and inspect the packet

Store each relevant raw artifact under the new evidence directory. Bind a
category once, using its relative path and the tool's hash calculation:

```bash
python3 validation/observe_native.py bind \
  ../native_evidence_01/NATIVE_OBSERVATION.json client_identity version_01/stdout.txt
python3 validation/observe_native.py check \
  ../native_evidence_01/NATIVE_OBSERVATION.json
```

`check` lists every missing category. An empty version log is not acceptable
identity evidence. Add the remaining R06 categories and, if observed, the R07
categories printed by the checker. Choose only the actions actually attempted.
The process-boundary artifact must state exactly what was tested and untested.
Keep protocol-era and native-tool-selection metadata consistent with that record.

Set `execution_kind: ACTUAL_NAMED_CLIENT` only for an actual named-client run.
The separate `OFFLINE_COLLECTOR_REHEARSAL` label is for exercising collection.
A fully bound rehearsal receives a different status and never becomes a native
observation. The check verifies snapshots, required nonempty files, identities
and explicit scope. It does not inspect the truth or completeness of prose logs,
prove producer identity, establish human acceptance or close an action. A reviewer
must reconstruct the journey against the original acceptance criteria.

## Rehearse collection without a coding client

From the companion root, use a fresh external directory:

```bash
python3 validation/rehearse_native_collection.py --output ../native_collection_rehearsal_01
python3 -B validation/test_native_collection.py
```

The rehearsal executes seven local commands: an absent executable, a missing
server script, a missing CLI argument, an unknown policy, a valid policy, an
explicit non-secret sibling-process canary read and Python's version command.
It retains all failures and verifies that an incomplete native packet is refused.
Its `PASS_LOCAL_REHEARSAL_ONLY` outcome concerns the collection machinery. No
model chooses a tool, no MCP SDK connects, and no named host is observed. The
separate trace-diagnosis commands above inspect the previously retained actual
SDK messages. These scopes remain separate in the reports.
