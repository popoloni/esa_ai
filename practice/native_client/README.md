# One bounded change in an installed coding client

[Home](../../README.md) · [Practice catalogue](../README.md) · [Chapter routes](../../navigation/CHAPTER_ROUTES.md)

For virtual-environment setup and the successful Apple Silicon guided CSV run,
follow the [detailed reproduction guide](REPRODUCE_GUIDED_CSV.md). It covers reuse
or fresh installation, effective permissions, prompts, independent checks and cleanup.

The Treasury router has a small but consequential defect: it sends zero and
negative amounts to the ordinary queue and raises an exception for some invalid
inputs. The approved Chapter 1 change is to reject those inputs while preserving
the EUR 5,000 boundary, the public API and `BR-001/v1`. The client may propose
that repair. A separate reader checks the result and decides whether to accept
it. Nothing in this exercise approves a payment.

This route uses **OpenCode 1.19.3** as the installed client and **Qwen3-4B
Q4_K_M** through a local **llama.cpp b11799** server. The retained observation
is under [observed/ch01_01/](observed/ch01_01/). In the fresh 22 October episode,
the guided recovery completed a source edit before its outer timeout. Independent
review then passed the original seven cases, fourteen additional planned cases
(with overlap), and the scope check. The native checker and final summary did
not complete; human acceptance remains pending. The packet includes unsuccessful
attempts as well as their recoveries. Native events and session exports show
what the client actually did; the surrounding recorder preserves commands and
file changes. The recorder does not impersonate the client.
A rerun is a new observation: its actions and outcome may differ even with
the same pinned components.

You can first read the observation without installing anything. To make your
own observation, follow the numbered route below. It is an optional extension
to Chapters 1 and 2; the standard-library exercises remain available separately.
Use a fresh Chapter 1 copy, then return to your cumulative working copy after
review. Do not replace completed work merely to reproduce a fault.

## 1. Understand the arrangement and its limits

There are four distinct components:

| Component | Job in this exercise | Evidence to inspect |
| --- | --- | --- |
| OpenCode | Sends model requests, offers tools, applies its tool permission rules and records a session | Actual version, effective configuration, native events and native export |
| Local model server | Generates responses using the downloaded model | Artifact hashes, launch arguments, server log and request results |
| Disposable companion copy | Holds the faulty router and the approved intent and tests | Starting bytes, before-edit baseline and final diff |
| Reader and recording tools | Capture execution, rerun checks and review the proposed change | Command receipts, protected-file checks and an explicit review decision |

The local endpoint is `http://127.0.0.1:18080/v1`. Model requests in the retained
run used that endpoint. This does **not** make the entire host offline: package
installation used public registries, and earlier d6 client attempts made background
npm requests that failed even with optional-plugin flags disabled. A localhost
model address describes the model route, not every possible connection made
by the application.

The client configuration limits native reads to named study files, edits to the
router and command execution to one acceptance command. These are application
controls. Neither the recorder nor the configuration creates an OS sandbox.
The effective agent also retains OpenCode's internal tool-output directory
exception; read the full effective rule list, not only a boolean tool summary.

Worked answers are shipped elsewhere in the companion. The author had prior
exposure to them; the native task did not authorize reading them or supply a
solution patch. The d7 recovery supplied the approved intent verbatim and explicit
`Decimal.is_finite()` guidance before ordering comparisons. This is a disclosed
teaching observation, not a blind model
benchmark. Human acceptance stays pending until an actual human reviews it.

## 2. Install the pinned local stack outside the companion

The retained environment is Linux x86-64 with Python 3.12.14. The commands below
use a POSIX shell, Python, Git, Node/npm and `tar`. Other operating systems and
runtime combinations are not established by this observation. The model file
alone is 2,497,280,256 bytes; allow additional disk and memory for the client,
server, model context and evidence. This is a CPU recipe, not a minimum-memory
or completion-time guarantee.

The Linux server also needs the OpenMP runtime. Minimal Debian/Ubuntu images may
not include it: if startup reports `libgomp.so.1: cannot open shared object file`,
install `libgomp1` using that environment's package manager (for example,
`sudo apt-get install libgomp1` on Debian/Ubuntu). In a container, install it
inside the container, not on the macOS/Windows host. The supplied Ubuntu archive
is x86-64; an ARM host needs a compatible Linux x86-64 environment for this exact
recipe. Do not substitute a different build and label it the same observation.

From the **unchanged companion root**, choose unused sibling directories:

```bash
export ESA_COMPANION="$(pwd)"
export ESA_RUNTIME="$(dirname "$ESA_COMPANION")/esa_native_runtime_01"
export ESA_WORK="$(dirname "$ESA_COMPANION")/esa_native_work_01"
export ESA_PACKET="$(dirname "$ESA_COMPANION")/esa_native_evidence_01"

mkdir -p "$ESA_RUNTIME/downloads" "$ESA_RUNTIME/llama_cpp" "$ESA_RUNTIME/opencode"
python3 -B practice/native_client/download_local_stack.py \
  --destination "$ESA_RUNTIME/downloads" \
  --evidence "$ESA_RUNTIME/download_receipts"
```

Proceed only when both download receipts say `PASS_HASH_VERIFIED`. The helper
uses fixed public URLs, preserves a failed partial download and refuses to
overwrite an attempt. It verifies these identities before producing the final
artifact names:

| Artifact | Pin | SHA-256 |
| --- | --- | --- |
| `llama-b11799-bin-ubuntu-x64.tar.gz` | Release b11799; commit `0756e83fc1529e207af783782905bc98a8ef0770` | `4920c65448350c28f8ce7b35eec91566807e0f111c25a0df2d5fc12a1ed1716a` |
| `Qwen3-4B-Q4_K_M.gguf` | Qwen repository revision `a9a60d009fa7ff9606305047c2bf77ac25dbec49` | `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5` |

Extract the verified release and install the exact client version. The separate
empty npm configuration files avoid inheriting a personal npm configuration;
they must have different paths. Use your approved registry/proxy and trusted
certificate setup. Preserve installation errors rather than disabling TLS
verification to get past them.

```bash
tar -xzf "$ESA_RUNTIME/downloads/llama-b11799-bin-ubuntu-x64.tar.gz" \
  -C "$ESA_RUNTIME/llama_cpp"
"$ESA_RUNTIME/llama_cpp/llama-b11799/llama-server" --version
python3 - <<'PY'
import os
from pathlib import Path
root = Path(os.environ['ESA_RUNTIME']) / 'opencode'
for name in ['npm-user.npmrc', 'npm-global.npmrc']:
    (root / name).open('x').close()
PY
npm --prefix "$ESA_RUNTIME/opencode" \
  --cache "$ESA_RUNTIME/opencode/npm-cache" \
  --userconfig "$ESA_RUNTIME/opencode/npm-user.npmrc" \
  --globalconfig "$ESA_RUNTIME/opencode/npm-global.npmrc" \
  install --no-audit --no-fund --save-exact --fetch-retries=0 opencode-ai@1.19.3
```

Keep the generated `package.json`, `package-lock.json` and installation output.
Require the server version check to succeed and identify build 11799 before
starting inference; resolve missing shared libraries or architecture errors first.
The supplied [setup/](setup/) receipts identify the author's installed package
and binary; your own version check is still required. The delivered companion
contains neither runtime binaries nor model weights.

Start the model server in a separate terminal using the same runtime path:

```bash
python3 -B practice/native_client/run_local_model.py \
  --runtime-root "$ESA_RUNTIME" --evidence "$ESA_RUNTIME/server_01"
```

This launcher records stdout, stderr and process lifecycle. It binds loopback
port 18080, uses eight CPU threads, a 16,384-token context, one request slot and
no GPU layers. Built-in server agent tools, its MCP proxy and web UI are disabled.
Starting the server loads the model; it does not itself submit a model request.
In the other terminal, check readiness without inference:

```bash
python3 - <<'PY'
import urllib.request
with urllib.request.urlopen('http://127.0.0.1:18080/health', timeout=10) as reply:
    print(reply.status, reply.read().decode())
PY
```

Expect HTTP 200 with `status: ok`. If startup or connection fails, retain the
server log and actual error. Check the executable, model hash, port and permitted
local networking before altering model or client settings. Stop the launcher
with Ctrl-C after the exercise so it can retain the final lifecycle receipt.

### Apple Silicon: avoid emulating the inference server

The Linux x86-64 recipe above remains unchanged. On an Apple Silicon host,
emulating that CPU-only server can consume most of the client deadline before
the first tool call. Both launchers now accept `--server-binary PATH` and
`--n-gpu-layers N`; the default is still the original runtime layout and CPU-only
execution (`0`). An explicit binary override is not automatic artifact verification.

For a native observation, use the **b11799 macOS ARM64** archive, not the Ubuntu
binary: [official release artifact](https://github.com/ggml-org/llama.cpp/releases/download/b11799/llama-b11799-bin-macos-arm64.tar.gz),
16,136,376 bytes, SHA-256
`51c3471c9212b41e51a6696c0b966628fa45d625385fdb024c4483e8d3154dca`.
Verify it before extraction and keep it separate from the Linux runtime. Install
OpenCode 1.19.3 for the native host in that separate prefix too; Linux executable
files and virtual environments cannot simply be reused on macOS. The verified
Qwen GGUF weights are platform-independent and need not be downloaded again.

For the existing verified runtime directories created by the execution audit,
run from the companion root, choosing a new evidence name:

```bash
export ESA_RUNTIME="$(cd ../esa_ai_native_runtime_darwin_01 && pwd)"
export ESA_MODEL_RUNTIME="$(cd ../esa_ai_native_runtime_01 && pwd)"
python3 -B practice/native_client/run_local_model_d8.py \
  --runtime-root "$ESA_MODEL_RUNTIME" \
  --server-binary "$ESA_RUNTIME/llama_cpp/llama-b11799/llama-server" \
  --n-gpu-layers 99 --ctx-size 16384 \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --threads 6 --batch-size 256 --ubatch-size 128 \
  --max-runtime-seconds 1500 --shutdown-grace-seconds 10 \
  --evidence "$ESA_RUNTIME/server_metal_NEW"
```

Confirm health and inspect the server log for actual Metal offload; a requested
GPU-layer count alone is not proof of acceleration. Use the native `ESA_RUNTIME`
for client configuration in the following steps. Keep the client task deadline
finite and shorter than the server's lifetime, with room for startup and review.
The receipts record the selected binary hash, host architecture and exact argv.
This is a separately observed macOS/Metal route, not a reproduction of the
historical Linux CPU runtime. Faster inference does not guarantee correct edits:
retain failed checks and independently review the resulting files. See the
[execution audit](../../validation/EXAMPLE_TEST_REPORT.md) for timings and outcomes.

## 3. Preserve the starting problem before asking for a repair

Back in the companion root:

```bash
python3 -B reader_start.py new 1 --destination "$ESA_WORK"
python3 -B validation/observe_native.py prepare \
  --source "$ESA_WORK" --output "$ESA_PACKET" --actions R06
cd "$ESA_WORK"
python3 -B reader_side/tools/scope_guard.py --chapter CP01 \
  --capture reader_side/evidence/CP01_NATIVE_BASELINE_01.json
python3 -B reader_side/tools/run_acceptance.py \
  --output reader_side/evidence/CH01_NATIVE_INITIAL_01.json
```

The acceptance command is expected to exit 1 with **3 passes, 2 failures and
2 errors**. That is the prepared defect, not a setup success inferred from a
green check. Open the result and distinguish an incorrect returned route from
an exception: the negative/zero cases fail expectations, while the malformed
and nonfinite cases expose missing validation. The protected-integrity fields
must be empty. If you receive a different starting state, investigate it before
continuing.

`starting_tree/` and `STARTING_MANIFEST.json` preserve the initial bytes and
identities. The scope baseline is created before editing and lists the router
as the sole editable source. Keep the packet outside the client's study copy.
A directory name alone does not enforce that separation against an arbitrary
process with the same OS permissions.

## 4. Generate and inspect the actual client configuration

Return to the untouched companion and prepare a new configuration directory:

```bash
cd "$ESA_COMPANION"
python3 -B practice/native_client/configure_chapter1.py \
  --work "$ESA_WORK" --runtime-root "$ESA_RUNTIME" \
  --output "$ESA_PACKET/configuration"
```

This helper performs no inference. It checks that the initial report and scope
baseline still identify the unchanged starter, locates the actual Git worktree,
and writes the configuration, exact task prompt and literal command arguments.
It refuses an existing output directory or a stale initial report. In the
observed non-Git case, pinned OpenCode 1.19.3 uses `/` as its permission worktree;
the helper generates the corresponding path keys. Moving the copy afterwards
invalidates those keys: prepare new configuration in a new directory.

Open `TASK_PROMPT.txt`. It supplies exact absolute paths, the approved change,
the preserved policy and the stopping condition. It does not include a code
solution. Open `OPENCODE_CONFIG.json` and locate the exact command allowance:

```text
python3 -B reader_side/tools/run_acceptance.py --output reader_side/evidence/CH01_NATIVE_AGENT_01.json
```

For **1.19.3**, the native tool and permission category are **`bash`**. A moving
documentation page describes `shell`; using that name in the earlier setup
parsed successfully but left the actual `bash` tool disabled. Configuration
parsing therefore does not establish the intended effective behavior. Retain
and inspect these installed-client diagnostics before starting a model task:

```bash
python3 -B validation/observe_native.py capture \
  --spec "$ESA_PACKET/configuration/VERSION_TASK.json" \
  --output "$ESA_PACKET/version"
python3 -B validation/observe_native.py capture \
  --spec "$ESA_PACKET/configuration/CONFIG_TASK.json" \
  --output "$ESA_PACKET/effective_config"
python3 -B validation/observe_native.py capture \
  --spec "$ESA_PACKET/configuration/AGENT_TASK.json" \
  --output "$ESA_PACKET/effective_agent"
```

Each directory contains the actual command, stdout, stderr, exit status and
before/after file inventory. Require version `1.19.3`, the local provider and
your own exact paths. The observed effective agent enables `bash`, `read`,
`edit` and `write`; its `edit` rules constrain the allowed destination. Other
displayed tools are disabled. Inspect the ordered rules and internal output
exception as well as these booleans. Stop if the effective result differs from
the intended scope.

The current helper sets both `timeout` and `headerTimeout` to 600,000 milliseconds,
with 2,048 output tokens and eight agent steps. The outer recorder allows 1,800
seconds. These are bounded study settings, not a promise that your hardware
will finish in that time. An earlier 180,000-millisecond request timed out after
successful file reads while the server was processing the next prompt. Its
failed request had no completed usage receipt; its token use remains unknown,
rather than being entered as zero.

These are separate provider controls in pinned OpenCode 1.19.3. The first native
SDD attempt set only `timeout=600000`; its independent default header deadline
still expired after 300,000 milliseconds. The repaired recipe sets both
explicitly. The SSE idle-chunk limit is another separate setting; it remains at
the pinned default. New configurations also include the upstream `$schema`
metadata before hashing, avoiding the client's later metadata-only insertion.
The observed configurations and preparation hashes remain as they were run;
see [the pinned source diagnosis](setup/runtime_d7/diagnosis/README.md).

The Chapter 1 recipe also sets `compaction.auto=false`. In the earlier continued
session, the host began automatic context compaction after a final-looking
failure message. Compaction condenses accumulated conversation and can itself
make model requests. The targeted setting disables that automatic activity for
this small bounded task; still observe the actual process exit. The generated
prompt now permits `READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED` only after all seven
cases pass with no integrity findings. A failed or incomplete task must be
reported without a readiness claim.

## 5. Run once, then inspect the task outcome

The following command invokes the actual installed client and therefore makes
local model requests. Review its specification first:

```bash
python3 -B validation/observe_native.py capture \
  --spec "$ESA_PACKET/configuration/CLIENT_TASK.json" \
  --output "$ESA_PACKET/attempt_01"
```

Read the native JSON events in `attempt_01/stdout.txt`, the client errors in
`stderr.txt` and the recorder's `RECEIPT.json`. Identify the files actually
read, each tool's completion or failure, any source change and any real
acceptance invocation. The recorder's `OBSERVED_COMMAND_SUCCESS` means that
the process returned zero. It does not mean that the requested repair passed.
In the historical d6 first attempt, the model omitted the study-directory segment
from five paths. The client's external-directory control refused all five
reads, the model stopped, and the CLI still exited zero. No source was changed.

Keep that distinction in your own outcome note: client exit status, task state,
observed checks and human review are separate fields. The prompt's intended
stop, `READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED`, cannot supply missing evidence.

### Export the native session without losing its tail

Export from the same client state and working directory. The recipe below
finds the one session ID actually present in the captured native events,
directs the export to a regular file, and then checks JSON and session identity.
It makes no model request. It refuses to overwrite an earlier export.

```bash
python3 - <<'PY'
import json, os, subprocess
from pathlib import Path
packet = Path(os.environ['ESA_PACKET'])
attempt = packet / 'attempt_01'
spec = json.loads((packet / 'configuration/CLIENT_TASK.json').read_text())
events = [json.loads(line) for line in (attempt / 'stdout.txt').read_text().splitlines() if line.strip()]
ids = {event['sessionID'] for event in events if event.get('sessionID')}
if len(ids) != 1:
    raise SystemExit('Expected exactly one observed session ID; inspect the native events.')
session_id = ids.pop()
argv = spec['argv'][:spec['argv'].index('run')] + ['export', session_id]
with (attempt / 'native-session.json').open('xb') as out, (attempt / 'export.stderr.txt').open('xb') as err:
    result = subprocess.run(argv, cwd=spec['cwd'], stdout=out, stderr=err, timeout=120)
(attempt / 'EXPORT_COMMAND.json').write_text(json.dumps({'argv': argv, 'cwd': spec['cwd'], 'exit_code': result.returncode}, indent=2) + '\n')
result.check_returncode()
exported = json.loads((attempt / 'native-session.json').read_text())
if exported.get('info', {}).get('id') != session_id:
    raise SystemExit('Export session identity differs from the captured events.')
print('Valid JSON export for', session_id)
PY
```

Why avoid a pipe here? One retained export exited zero but stopped at exactly
65,536 bytes and was invalid JSON. Repeating the same native export with stdout
directed to a regular file produced a complete, identity-checked export. Both
versions and the recovery are retained. If your export fails, keep its bytes
and use new output filenames for the correction; do not quietly replace it.

## 6. Recover at the layer that failed

| Actual symptom | Question to answer | Bounded next step |
| --- | --- | --- |
| Configuration parses but the expected tool is disabled | Does this installed release recognize the permission name? | Compare the effective agent with the pinned version; preserve the old configuration before correcting `shell` to `bash` for 1.19.3 |
| Native read is refused | What exact path did the model request, and what rule refused it? | Supply the correct allowed absolute path; retain the refusal and preserve the allowlist |
| Request times out after successful reads | Did the server start, receive the request and make progress? | Retain client error and server log; choose a declared new request budget without changing task authority or supplying a solution |
| Client exits zero without an edit or a check | What did the native tools actually complete? | Record `TASK_NOT_COMPLETED`; diagnose the last observed step before starting a separate attempt |
| Export exits zero but does not parse | Was all stdout retained? | Export to a new regular file, parse JSON and verify its session ID |
| Candidate fails an independent check | Which approved case still fails, or which protected file changed? | Preserve the candidate and result; issue a bounded correction or stop for review |

Use a new task specification and output directory for every continuation. Keep
the previous prompt, configuration and result. To continue an actual OpenCode
session, its pinned `run --help` exposes `--session`; use the session ID from
your native events. A fresh session and a continuation have different context,
so say which you chose. Do not turn a timeout into an unexplained permission
expansion or treat an interrupted request as free work.

For a correction within the **unchanged** configuration and command scope,
write `RECOVERY_PROMPT_02.txt` in your evidence packet. State the actual failure,
point to the allowed source or report, retain the approved intent and ask for
one bounded correction. Do not assert that a read or check succeeded unless
the native events show it. Then prepare a continuation without running it:

```bash
python3 - <<'PY'
import json, os
from pathlib import Path
packet, work = Path(os.environ['ESA_PACKET']), Path(os.environ['ESA_WORK'])
attempt = packet / 'attempt_01'
events = [json.loads(line) for line in (attempt / 'stdout.txt').read_text().splitlines() if line.strip()]
ids = {event['sessionID'] for event in events if event.get('sessionID')}
if len(ids) != 1:
    raise SystemExit('Inspect the actual session identity before continuing.')
spec = json.loads((packet / 'configuration/CLIENT_TASK.json').read_text())
prompt = (packet / 'RECOVERY_PROMPT_02.txt').read_text()
if not prompt.strip():
    raise SystemExit('The recovery prompt is empty.')
for source, retained in [('repo/src/treasury/routing.py', 'routing.py'),
                         ('reader_side/evidence/CH01_NATIVE_AGENT_01.json', 'acceptance-result.json')]:
    if (work / source).exists():
        with (attempt / retained).open('xb') as output:
            output.write((work / source).read_bytes())
spec['origin'] = 'reader_bounded_continuation'
spec['argv'] = spec['argv'][:-1] + ['--session', ids.pop(), prompt]
with (packet / 'CLIENT_TASK_02.json').open('x') as output:
    json.dump(spec, output, indent=2)
    output.write('\n')
print('Continuation prepared; no model request made.')
PY
```

Inspect `CLIENT_TASK_02.json`, then execute the continuation as its own attempt:

```bash
python3 -B validation/observe_native.py capture \
  --spec "$ESA_PACKET/CLIENT_TASK_02.json" \
  --output "$ESA_PACKET/attempt_02"
```

The separate source/report copies matter: the acceptance runner writes to its
named output, so a later invocation can replace that file in the study copy.
The completed attempt's preserved bytes remain the evidence for its failure.
Export the new attempt using the same direct-file recipe with its new attempt directory.
This continuation procedure preserves client state and permissions; changing
the configuration requires a separately retained version and fresh effective
diagnostics. The fresh-starter helper deliberately refuses a repaired candidate
and should not be used to relabel a continuation as a new blind start.

## 7. Check the candidate outside its completion message

After the client stops, run the reader's checks from the study root. They create
a new result rather than reusing or overwriting the agent's report:

```bash
cd "$ESA_WORK"
python3 -B reader_side/tools/run_acceptance.py \
  --output reader_side/evidence/CH01_NATIVE_REVIEW_01.json
python3 -B reader_side/tools/scope_guard.py --chapter CP01 \
  --baseline reader_side/evidence/CP01_NATIVE_BASELINE_01.json
git diff --no-index -- \
  "$ESA_PACKET/starting_tree/repo/src/treasury/routing.py" \
  repo/src/treasury/routing.py
```

`git diff --no-index` works without a Git repository. Exit 1 normally means that
there is a diff to review. Confirm that a passing acceptance result has seven
cases and no protected-integrity findings, then inspect the actual change
against the approved intent. An unchanged faulty candidate still fails; a
client's assertion does not alter that result.

The external checker detects selected scope and integrity violations when the
reader runs it. It cannot protect itself against a process with unrestricted
OS access. Record who reviewed the diff and whether that reviewer was human
or an assistant. A passing local check can support a proposal for acceptance;
it cannot supply an unperformed human decision.

The generic packet's `bind` and `check` commands are documented in
[NATIVE_HOST_COLLECTION.md](../../validation/NATIVE_HOST_COLLECTION.md). They
connect required evidence to hashes and detect missing or changed records.
Their result concerns consistency, not producer authentication, OS containment,
business acceptance or a performance comparison.

## 8. Connect the same client to a read-only policy lookup

The next task exercises a different capability. Ask the client to retrieve a
policy through the existing MCP tool, distinguish an unknown identifier from
an invalid argument, and stop. It needs no code editor or shell tool. Reading
`BR-001/v2` explains the future policy record; it does not authorize applying
that version to the Chapter 1 router.

Use the unchanged server, catalog and relay from `practice/mcp_cli/`. The
optional Python environment is separate from both the companion and OpenCode.
The retained setup used `uv` with an explicit local cache and the existing
28-package version lock. With `uv` and the intended Python already installed,
run from the companion root:

```bash
UV_CACHE_DIR="$ESA_RUNTIME/mcp_cache" UV_PYTHON_DOWNLOADS=never \
  uv venv --python "$(command -v python3)" "$ESA_RUNTIME/mcp_venv"
UV_CACHE_DIR="$ESA_RUNTIME/mcp_cache" UV_PYTHON_DOWNLOADS=never \
  uv pip install --python "$ESA_RUNTIME/mcp_venv/bin/python" \
  --index-url https://pypi.org/simple \
  --requirement practice/mcp_cli/requirements.lock
"$ESA_RUNTIME/mcp_venv/bin/python" -c \
  'import importlib.metadata, platform; print(platform.python_version()); print(importlib.metadata.version("mcp"))'
```

Retain the installation output and installed versions. The observed Python is
3.12.14 and the required SDK is 2.3.0; the lock names all dependencies rather
than attesting wheel hashes. Use an unused environment. The prior SDK-only
comparison in [mcp_cli/README.md](../mcp_cli/README.md) is still a separate
observation with its own protocol trace.

Prepare a new host observation, leaving the routing study intact:

```bash
export ESA_MCP_WORK="$(dirname "$ESA_COMPANION")/esa_mcp_work_01"
export ESA_MCP_PACKET="$(dirname "$ESA_COMPANION")/esa_mcp_evidence_01"
python3 -B practice/native_client/configure_mcp.py \
  --work "$ESA_MCP_WORK" --runtime-root "$ESA_RUNTIME" \
  --output "$ESA_MCP_PACKET"
```

The helper creates the two new directories, starting snapshot, host
configuration, prompt, recorder task and one declared non-secret canary. It
does not launch a server, submit a model request or read the canary. Inspect
`OPENCODE_CONFIG.json`, `TASK_PROMPT.txt` and `CANARY_DECLARATION.json` before
running the observation. Only `treasury_lookup_policy` is allowed as a native
tool. The local MCP command uses the pinned Python to run the canonical
`wire_proxy.py`, which launches its sibling `policy_server.py` and retains the
actual request/response lines. The relay is a recorder, not a sandbox.

The prompt requests three outcomes: a real `BR-001/v2` result, an
`UNKNOWN_POLICY` response for the well-formed identifier `BR-999/v1`, and one
attempt with the deliberately wrong argument type `policy_id: []`. It tells
the model to report a host-side rejection honestly if the invalid call never
reaches the server. Substituting a string and calling it a schema error would
answer a different question.

### Inspect one declared process boundary

The opt-in startup probe is instrumentation of the **serving Python process**.
A task-local `sitecustomize.py` runs only when that interpreter enters the
canonical server, reads the one declared non-secret file outside the study
and server directories, and records process identifiers and source/result
hashes. It adds no MCP tool and writes no protocol stdout. The canonical server
and relay stay unchanged, but the instrumented runtime is deliberately
different from a launch without the hook.

This probe asks whether that actual serving process can read that one path at
startup. A successful read is an observed limit of the process boundary; it
does not grant the model an arbitrary-file tool. A missing record means that
the read was not observed, not that the OS denied it. Network, inherited
secrets, external writes and any later isolation remain untested by this probe.

With the local model healthy and the prepared configuration reviewed, capture
one host launch:

```bash
python3 -B validation/observe_native.py capture \
  --spec "$ESA_MCP_PACKET/CLIENT_TASK.json" \
  --output "$ESA_MCP_PACKET/attempt_01"
```

Do not first run a diagnostic that starts this MCP server against the same
configuration. The relay opens its trace files exclusively; a diagnostic and
a model session can be different server processes. Prepare a new work and
evidence pair for each new launch rather than deleting earlier traces.

Read the host's native events together with `trace_01/client_to_server.jsonl`
and `server_to_client.jsonl`. Locate the opening exchange, actual protocol,
`tools/list` and calls by request/response ID. The native name includes the
configured server prefix (`treasury_lookup_policy`); the MCP wire tool is
`lookup_policy`. Match the arguments and outcomes before attributing a result
to the model's action. Inspect the startup-probe record separately.

Export the native session using the direct-file recipe above, selecting
`ESA_MCP_PACKET` as the packet and its root `CLIENT_TASK.json` as the task.
Parse the export and verify the session ID. A connection, tool discovery and a
model-selected call establish different steps; preserve any absent step as
unobserved. The retained host episode is under
[observed/mcp_host_01/](observed/mcp_host_01/).

## 9. Read the retained observation

Start with the episode's outcome and independent checks, then follow the native
events for any conclusion you want to verify. Use the full exported session for
context and `starting_files/` for the relevant initial source. The complete
1,584-file starting snapshot and its manifest remain in the author archive;
the portable packet includes the original manifest and the files needed to
inspect this repair. Absolute paths in those
historical records identify the author's machine; generate relocated settings
with the helper for your own copy.

### Fresh d7 episode: a checked repair after an unfinished native run

The runtime was reconstructed from the pinned artifacts on 22 October 2026;
the earlier machine and its active excluded attempt were unavailable. The
reconstruction receipts are under [setup/runtime_d7/](setup/runtime_d7/).
This is a new observation with its own starting copy and session identifiers.

| Stage | Native actions and process result | Independent interpretation |
| --- | --- | --- |
| Initial state | Faulty router; seven cases produce three passes, two failures and two errors | Original intent and test hashes retained |
| d7 attempt 01 | Read router, then ran acceptance before editing; same failing result. Operator stopped the next model request after 555.556 seconds; exit -2 | No source change; preserve first output and failed check |
| d7 attempt 02 | Fresh session with explicit finite-value guidance. Read router, then completed an `edit` replacing the function body. Outer 360-second bound returned exit 124 after 360.108 seconds | Source edit completed; requested native checker and final summary did not complete |
| Independent review | Reader reran the original seven cases, fourteen predeclared additional cases and scope guard | Both case sets and scope check passed; the sets overlap. Agent disposition: `READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED` |

The recovery prompt requested the `write` tool; the observed client chose the
allowed `edit` tool. The retained native diff and independently read candidate
match. No ready-made implementation patch was supplied. The change rejects
malformed, nonfinite and nonpositive values while preserving the policy version,
return type and EUR 5,000 boundary. Its SHA-256 is
`dac968f4738761cc85a6b71f0d7265a2d8d1860f122cd22576a9645bc9139fe7`.
Read [the packet index](observed/ch01_01/README.md),
[the final diff](observed/ch01_01/independent_review/routing.diff) and
[the independent disposition](observed/ch01_01/independent_review/REVIEW.json).

The actual read event also exposes automatic instruction loading: a 671-byte
router produced 9,077 characters of tool output because OpenCode appended the
repository's integrated Chapters 1–14 `AGENTS.md`. The native metadata names
that loaded file. This establishes what context was returned, not why the
model chose its actions or why a request timed out. The retained server prefix
contains four completed request timings and two later interrupted requests.
Three resource samples show the shared host near its 8 GiB memory limit without
an observed OOM kill. They do not establish a hardware minimum or controlled
performance comparison. The explicit observation overrides used outer bounds
of 600 and 360 seconds; the general recipe's longer default remains separate.

### Historical d6 failures retained separately

The `historical_d6/` extract preserves the earlier records without rewriting
them as this fresh episode. Its first attempt stopped at five refused reads. The next used the
correct paths and completed all five reads, then hit the 180-second provider
deadline before editing. The correction retained those failures and changed
the request budget to 600 seconds. The third attempt edited the authorized
router and invoked the exact acceptance command. It reached **six passes and
one error**: converting `NaN` to `Decimal` did not reject it, and the subsequent
comparison raised `InvalidOperation`. Source review also found an unreachable
copy of the old function body after an unconditional return. The model ended
with the requested readiness phrase despite the failed check. The outcome
therefore remains `FAILED_ACCEPTANCE`; the wording did not overrule the test.

The next bounded continuation pointed to that actual report and current
candidate without supplying a replacement patch. Its new insertion repeated
the problem: six cases passed and the nonfinite case still errored, with
duplicate old code remaining. This time the native summary correctly said
`FAILED_ACCEPTANCE`. The host subsequently began automatic context compaction.
The operator interrupted that continued activity; the retained receipt records
exit -15 and `FAILED_ACCEPTANCE_INTERRUPTED_DURING_COMPACTION`. Only the allowed
candidate and generated report changed. Final-looking prose therefore did not
establish that the host had stopped making model requests; actual process
completion, the intervention and the further events are retained separately.

The resulting recovery decision was to use a fresh session, request a single
complete function, and supply explicit API-level guidance from the
[Python 3.12 `Decimal.is_finite()` documentation](https://docs.python.org/3.12/library/decimal.html#decimal.Decimal.is_finite):
reject NaN and infinities before ordering comparisons. The recovered configuration disables automatic
compaction. That assistance and setting change must be disclosed alongside
the resulting candidate. No failed attempt is silently counted as a completed
repair. The following d6 attempt was also interrupted without a source change.
The then-active d6 attempt 06 was excluded from CP11, so its outcome remains
unknown. The fresh d7 recovery above does not establish what happened to it.

Native `step_finish` events expose usage for completed steps. Choose either
those step records or an explicitly corresponding session total; adding both
would double count the same work. Failed requests without a completed receipt
remain unknown. OpenCode's application `cost: 0` does not measure electricity,
machine allocation, the surrounding author/reviewer work or total financial
cost. This exercise supports no cost or speed ranking.

## 10. Compare an unobserved IDE route honestly

VS Code with GitHub Copilot is the **unobserved contrast**. GitHub's
[agent-mode guide](https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-agent-mode)
describes streamed editor changes and command approval by default, with editor
or administrator settings able to permit automatic execution. Our observed
OpenCode route uses a literal noninteractive command and a predeclared exact
command allowance. This changes how the operator reviews tool execution and
collects evidence; it does not establish that either product is more capable.

To observe that contrast, use a separate fresh copy, the same intent and scope,
and retain the actual editor, extension and exposed model versions, effective
settings, prompts, tool activity and independent checks. The supplied blank
Copilot/Claude records remain unperformed until those products are actually
used. No paired performance result follows from the single OpenCode route.

## Sources and maintenance

The author's pinned identities, effective diagnostics, installation failures
and recoveries are retained under [setup/](setup/) and [observed/](observed/).
The following primary sources were checked on 21 October 2026:

- [OpenCode CLI reference](https://opencode.ai/docs/cli/) and
  [provider configuration](https://opencode.ai/docs/providers/) explain the
  product entry points. Moving pages are not a substitute for the installed
  1.19.3 diagnostics.
- The pinned [native shell tool ID](https://raw.githubusercontent.com/anomalyco/opencode/v1.19.3/packages/opencode/src/tool/shell/id.ts)
  and [V1 permission configuration](https://raw.githubusercontent.com/anomalyco/opencode/v1.19.3/packages/core/src/v1/config/permission.ts)
  identify the release-specific `bash` spelling.
- [llama.cpp release b11799](https://github.com/ggml-org/llama.cpp/releases/tag/b11799)
  and the [pinned Qwen model file](https://huggingface.co/Qwen/Qwen3-4B-GGUF/blob/a9a60d009fa7ff9606305047c2bf77ac25dbec49/Qwen3-4B-Q4_K_M.gguf)
  identify the downloaded public artifacts.

Upgrade one component in a new runtime and fresh study copy. Retain the earlier
observation, rerun effective-configuration checks, record the actual protocol
and tool results, and explain the changed behavior before extending this recipe
to another version.
