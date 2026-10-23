# Reproduce the local LLM-assisted CSV repair

[Home](../../README.md) · [Native client setup](README.md) · [CSV journey](../native_journey/README.md) · [Execution report](../../validation/EXAMPLE_TEST_REPORT.md)

This guide reproduces the **workflow** that produced a passing, explicitly guided
CSV implementation on Apple Silicon. It covers isolated Python environments,
the pinned native inference server and coding client, fresh task preparation,
guided implementation, independent checks, and shutdown. It does not promise
identical model output or execution times.

The successful observation reused Qwen3-4B Q4_K_M, llama.cpp **b11799**,
OpenCode **1.19.3**, Python **3.12.4**, and Metal on an Apple M2 Max with 64 GiB
RAM. Implementation took 24.856 seconds; a documents-only continuation took
27.330 seconds. Final results were **7/7 contract checks, 17/17 independent
checks and both demos passing**. The plan retained a stale intermediate finding:
a technical pass is not proof of perfect prose, human acceptance or production readiness.

## 1. Choose the route and understand the boundaries

- **Existing installation on this workstation:** reuse the Python environment and
  native runtime in section 2; do not download weights or reinstall tools.
- **New Apple Silicon installation:** create the environments, then follow section 3.
- **Linux x86-64:** use the original [pinned Linux setup](README.md#2-install-the-pinned-local-stack-outside-the-companion).
  That archive needs a compatible Linux runtime (including OpenMP). A macOS
  virtual environment cannot be reused inside Linux.
- **Intel Mac, Windows or other hardware:** not certified by this observation.
  Do not use the Darwin ARM64 binary on an incompatible host.

The earlier emulated Linux x86-64 run on Apple Silicon hit 900 seconds. Native
Metal removed that practical bottleneck. A matched 3,404-token cold prompt took
91.998 seconds to process on native CPU and 4.795 seconds on Metal. This single
sample is not a universal benchmark or a minimum-resource guarantee.

There are three separate environments:

| Environment | Contains | Does not contain |
| --- | --- | --- |
| Python venv | Python tools, optional test dependencies | Model weights, llama.cpp, OpenCode |
| Native runtime directory | Verified model/server, isolated npm client | Learner source or accepted results |
| Fresh project/state/evidence | Disposable starter, client configuration/session, exact prompts and checks | Permission to change the shipped starter or checker |

The client uses a loopback model endpoint, but application tool permissions are
**not an OS sandbox**. Installation requires network access; a local endpoint
does not prove all client activity is offline. Do not use production data or secrets.

## 2. Python environments and paths

Use a POSIX shell (zsh/bash). Start in your official checkout. The example local
path is this workstation's path; change it on another machine. Prefer paths
without spaces: the helper constructs an exact permitted shell checker command.

```bash
cd /Users/enricopapalini/local_repos/esa_ai
export ESA_REPO="$(pwd -P)"
export ESA_PARENT="$(dirname "$ESA_REPO")"
export ESA_PY_ENV="$ESA_PARENT/esa_ai_test_env"
export ESA_RUNTIME="$ESA_PARENT/esa_ai_native_runtime_darwin_01"
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/private/tmp
```

On Linux use `TMPDIR=/tmp`. On macOS use canonical `/private/tmp` paths to avoid
root-alias receipt mismatches. Do not change protected manifests to bypass a failure.

### Reuse the existing environment

```bash
"$ESA_PY_ENV/bin/python" --version
"$ESA_PY_ENV/bin/python" -m pip check
export PATH="$ESA_PY_ENV/bin:$PATH"
command -v python3
python3 --version
```

Require Python 3.12 for this reproduction; the observed host interpreter was
3.12.4. Prepending the venv matters: the native client's allowed check invokes
`python3`, not a hardcoded venv interpreter. No activation is otherwise needed.
If you prefer activation, `source "$ESA_PY_ENV/bin/activate"` is equivalent for
interactive use; use `deactivate` when done.

### Create a new environment only if none exists

Install Python 3.12, Git, Node/npm and the platform's required runtime tools using
your approved installation process first. This guide does not modify your system
package manager. Verify `python3.12 --version`, `git --version`,
`node --version`, `npm --version`, and `uname -sm`; retain these outputs.

Use a new path instead of overwriting an existing environment:

```bash
test ! -e "$ESA_PY_ENV" &&
  python3.12 -m venv "$ESA_PY_ENV"
export PATH="$ESA_PY_ENV/bin:$PATH"
"$ESA_PY_ENV/bin/python" -m pip check
```

The CSV exercise, recorder, launcher and independent reviewer use the Python
standard library. **No pip packages are required for the CSV route.**

For the broader audit, keep optional dependency groups separate:

| Purpose | Environment example | Retained dependency source |
| --- | --- | --- |
| Verification tools (Hypothesis/Bandit) | `esa_ai_verify_env` | [verification requirements](../verification_tools/requirements.txt) |
| MCP SDK tests/configuration | `esa_ai_mcp_env` | [full MCP lock](../mcp_cli/requirements.lock) |
| Spec Kit CLI 1.2.2 | `esa_ai_specify_env` | [full Spec Kit lock](../sdd/evidence/toolchain/python_requirements.lock.txt) |
| OpenCode / optional OpenSpec | Isolated npm prefix, not a Python venv | [native setup](README.md), [SDD CLI guide](../sdd/CLI_REPRODUCTION.md) |

Optional installation commands (choose unused paths; skip for CSV):

```bash
python3.12 -m venv "$ESA_PARENT/esa_ai_verify_env"
"$ESA_PARENT/esa_ai_verify_env/bin/python" -m pip install -r "$ESA_REPO/practice/verification_tools/requirements.txt"
"$ESA_PARENT/esa_ai_verify_env/bin/python" -m pip check

python3.12 -m venv "$ESA_PARENT/esa_ai_mcp_env"
"$ESA_PARENT/esa_ai_mcp_env/bin/python" -m pip install -r "$ESA_REPO/practice/mcp_cli/requirements.lock"
"$ESA_PARENT/esa_ai_mcp_env/bin/python" -m pip check

python3.12 -m venv "$ESA_PARENT/esa_ai_specify_env"
"$ESA_PARENT/esa_ai_specify_env/bin/python" -m pip install -r "$ESA_REPO/practice/sdd/evidence/toolchain/python_requirements.lock.txt"
"$ESA_PARENT/esa_ai_specify_env/bin/python" -m pip check
"$ESA_PARENT/esa_ai_specify_env/bin/specify" --version
```

Keep installation stdout/stderr and `python -m pip freeze` output for each
environment in your new evidence directory. A top-level package pin does not pin
transitives: the audit initially found three newer Spec Kit transitives and
reinstalled from the full lock. The retained locks describe a specific observed
installation, not guaranteed availability or compatibility on every platform.
If resolution fails, retain the failure; do not silently unpin dependencies.
Do not copy venvs across operating systems. Follow the [SDD guide](../sdd/CLI_REPRODUCTION.md)
for scaffold tests; this CSV workflow does not establish live SDD generation.

## 3. Native runtime: reuse first, install only if necessary

### Existing runtime

The original Linux runtime contains the same OS-independent weights; the Darwin
runtime already exposes them under its own downloads directory. Verify rather
than downloading again:

```bash
shasum -a 256 "$ESA_RUNTIME/downloads/Qwen3-4B-Q4_K_M.gguf"
shasum -a 256 "$ESA_RUNTIME/downloads/llama-b11799-bin-macos-arm64.tar.gz"
"$ESA_RUNTIME/llama_cpp/llama-b11799/llama-server" --version
"$ESA_RUNTIME/opencode/node_modules/.bin/opencode" --version
```

Required identities:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Qwen3-4B-Q4_K_M.gguf | 2,497,280,256 | `7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5` |
| llama-b11799-bin-macos-arm64.tar.gz | 16,136,376 | `51c3471c9212b41e51a6696c0b966628fa45d625385fdb024c4483e8d3154dca` |

Require build 11799 / commit `0756e83fc` and OpenCode 1.19.3. The verified Darwin
server executable in this observation hashed to
`981b460a278e9a0c880cef32d6fab42785a119084456b16845304cf38c32cf69`.
The launcher's explicit binary override records identity; it does not itself
certify that an arbitrary binary matches these pins.

### Fresh Darwin ARM64 runtime

Skip this subsection if section 3's verification passed. Choose a new
`ESA_RUNTIME` path. The following snippet reuses the existing downloader's
streaming hash verification but selects the verified Darwin archive and the
pinned model. It downloads about 2.5 GB and preserves failure receipts; it does
not invoke a model.

```bash
test ! -e "$ESA_RUNTIME" && mkdir "$ESA_RUNTIME"
"$ESA_PY_ENV/bin/python" -B - <<'PY'
import os, runpy
from pathlib import Path
repo = Path(os.environ["ESA_REPO"])
runtime = Path(os.environ["ESA_RUNTIME"])
helper = runpy.run_path(str(repo / "practice/native_client/download_local_stack.py"))
model = dict(helper["ARTIFACTS"][1], expected_bytes=2497280256)
server = dict(helper["ARTIFACTS"][0],
    name="llama-b11799-bin-macos-arm64.tar.gz",
    url="https://github.com/ggml-org/llama.cpp/releases/download/b11799/llama-b11799-bin-macos-arm64.tar.gz",
    sha256="51c3471c9212b41e51a6696c0b966628fa45d625385fdb024c4483e8d3154dca",
    expected_bytes=16136376)
(runtime / "downloads").mkdir(exist_ok=True)
for artifact in (server, model):
    if not helper["download"](artifact, runtime / "downloads", runtime / "download_receipts"):
        raise SystemExit("Download failed; retain evidence and stop.")
PY
```

Require both receipts to say `PASS_HASH_VERIFIED` before extraction. Reuse
already verified weights via a link to their canonical location if desired,
instead of running the model download again; the expected filename must remain
`downloads/Qwen3-4B-Q4_K_M.gguf`. Do not mix Darwin executables with Linux ones.

```bash
mkdir -p "$ESA_RUNTIME/llama_cpp" "$ESA_RUNTIME/opencode"
tar -xzf "$ESA_RUNTIME/downloads/llama-b11799-bin-macos-arm64.tar.gz" -C "$ESA_RUNTIME/llama_cpp"
"$ESA_RUNTIME/llama_cpp/llama-b11799/llama-server" --version
touch "$ESA_RUNTIME/opencode/npm-user.npmrc" "$ESA_RUNTIME/opencode/npm-global.npmrc"
npm --prefix "$ESA_RUNTIME/opencode" \
  --cache "$ESA_RUNTIME/opencode/npm-cache" \
  --userconfig "$ESA_RUNTIME/opencode/npm-user.npmrc" \
  --globalconfig "$ESA_RUNTIME/opencode/npm-global.npmrc" \
  install --no-audit --no-fund --save-exact --fetch-retries=0 opencode-ai@1.19.3
"$ESA_RUNTIME/opencode/node_modules/.bin/opencode" --version
```

Use distinct empty npm user/global config files in this fresh prefix. Retain the
generated package lock and install logs. This pins the client version but does
not promise the same transitive resolution as a historical npm lock. Do not
disable TLS verification to work around registry/certificate failures.

## 4. Check the checkout, then prepare a new project

Run these from the official repository, not inside a previous candidate:

```bash
cd "$ESA_REPO"
"$ESA_PY_ENV/bin/python" -B reader_start.py doctor
"$ESA_PY_ENV/bin/python" -B -m unittest discover -s validation -p 'test_*.py' -v
export ESA_RUN="$ESA_PARENT/esa_ai_csv_reproduction_01"
test ! -e "$ESA_RUN" && mkdir "$ESA_RUN"
export ESA_PROJECT="$ESA_RUN/project"
export ESA_PREP="$ESA_RUN/preparation"
"$ESA_PY_ENV/bin/python" -B practice/native_journey/prepare_observation.py \
  --companion "$ESA_REPO" --runtime "$ESA_RUNTIME" \
  --project "$ESA_PROJECT" --state "$ESA_RUN/state" --evidence "$ESA_PREP"
```

Stop if doctor reports protected/starter findings. The validation suite currently
has 17 tests. Preparation must report `no_inference: true`, unchanged starter
bytes and the **expected initial checker exit 1** because CSV is unimplemented.
It preserves the initial check and starting manifest. The project must not be
inside a Git worktree: the configured permission keys assume this non-Git layout.
Do not run `git init` in it.

The initial permission set allows only selected files. To reproduce the guided
repair, preserve the initial config and add read access to the actual selection
and contract files, leaving write permissions untouched. Replace the task prompt
with the disclosed guided instructions below.

```bash
"$ESA_PY_ENV/bin/python" -B - <<'PY'
import hashlib, json, os, shutil
from pathlib import Path
prep = Path(os.environ["ESA_PREP"])
project = Path(os.environ["ESA_PROJECT"])
run = Path(os.environ["ESA_RUN"])
config_path = prep / "OPENCODE_CONFIG.json"
backup = prep / "OPENCODE_CONFIG.original.json"
if backup.exists():
    raise SystemExit("Already customized; use a fresh run.")
shutil.copy2(config_path, backup)
config = json.loads(config_path.read_text())
prefix = project.as_posix().lstrip("/") + "/"
for name in ("selection.py", "CURRENT_CONTRACT.md"):
    config["permission"]["read"][prefix + name] = "allow"
config_path.write_text(json.dumps(config, indent=2) + "\n")
task = json.loads((prep / "CLIENT_TASK.json").read_text())
checker = json.loads((prep / "PROTOCOL.json").read_text())["checker"]
command = " ".join(checker["argv"])
prompt = f"""Guided CSV implementation on a FRESH unchanged starter.
First use read tools to read {project}/api.py, {project}/selection.py and
{project}/CURRENT_CONTRACT.md BEFORE editing. State the selection dependency
and constraints. Preserve the exact orders_response(rows, actor,
format="json", status=None) signature and JSON behavior.
Implement the simplest inline CSV branch in that existing function.
Use the same selected_orders authority and public fields. Use standard-library
csv.writer with io.StringIO for escaping and a header even for empty results.
Do not hand-join fields, invent helper APIs or delete orders_response.
Define/import every name used. No reference solution is supplied.
Write concise spec.md and plan.md naming the contract and fictional
CSV-CONSUMER-01 decision. Do not claim real owner approval.
Only api.py, optional presenter.py, spec.md and plan.md may change.
No packages. Run exactly this permitted checker using bash:
{command}
Inspect actual results, correct allowed code if necessary and report accurately.
The invocation has a 900-second outer bound and 12-step configuration.
Previous failures deleted the API and duplicated helpers: avoid those failures."""
prompt_path = run / "PROMPT_01.txt"
prompt_path.write_text(prompt)
task["argv"][-1] = prompt
task["prompt_reference"] = str(prompt_path)
task["prompt_sha256"] = hashlib.sha256(prompt.encode()).hexdigest()
(run / "TASK_01.json").write_text(json.dumps(task, indent=2) + "\n")
(run / "INTERVENTION.json").write_text(json.dumps({
    "guidance": "Fresh starter; preserve API; inline csv.writer/io.StringIO",
    "read_permissions_added": ["selection.py", "CURRENT_CONTRACT.md"],
    "write_permissions_unchanged": True, "checker_unchanged": True,
    "maximum_attempts": 3, "per_attempt_seconds": 900,
    "reference_solution_supplied": False,
    "note": "Adapted reproduction prompt; exact historical prompt is in the retained packet."
}, indent=2) + "\n")
PY
```

This prompt is an adapted, path-independent version of the successful guidance,
not a claim of byte-identical historical replay. The exact original prompts are
in the retained packet described in section 10.

**Important recorder behavior:** [run_observation.py](../native_journey/run_observation.py)
always loads `ESA_PREP/ENVIRONMENT.json`. Changing a task's
`environment_reference` alone does nothing. That preparation environment names
the config through `OPENCODE_CONFIG`. Earlier attempts proposed a different
environment without actually applying it; do not repeat that mistake.

Capture the **effective** config/agent after the change using the actual environment:

```bash
"$ESA_PY_ENV/bin/python" -B - <<'PY'
import json, os, subprocess
from pathlib import Path
prep = Path(os.environ["ESA_PREP"])
env = json.loads((prep / "ENVIRONMENT.json").read_text())
binary = str(Path(os.environ["ESA_RUNTIME"]) / "opencode/node_modules/.bin/opencode")
for name, args in (("config", ["config"]), ("agent", ["agent", "esa-csv"])):
    with (prep / f"guided-effective-{name}.stdout.txt").open("xb") as out, \
         (prep / f"guided-effective-{name}.stderr.txt").open("xb") as err:
        subprocess.run([binary, "--pure", "debug", *args],
                       cwd=os.environ["ESA_PROJECT"], env=env,
                       stdout=out, stderr=err, timeout=90, check=True)
PY
```

Inspect these files: model is `esa-local/esa-qwen3-4b`, temperature capability
enabled with agent temperature 0.2, context 16,384, output limit 2,048, steps 12,
and reads/writes/bash limited as declared. This client also has internal
tool-output path rules; inspect them rather than treating these as OS isolation.
In OpenCode 1.19.3, write/edit/apply_patch share edit permission; an edit-only
disable retaining write is not supported through the investigated settings.

## 5. Start the native server in a separate terminal

Reuse the exported paths in the new terminal (or set them explicitly there).
Shell exports do not automatically propagate into an independently opened terminal.
Check port 18080 first with `lsof -nP -iTCP:18080 -sTCP:LISTEN`; if occupied,
identify its owner. Never kill an unrelated server.

```bash
"$ESA_PY_ENV/bin/python" -B "$ESA_REPO/practice/native_client/run_local_model_d8.py" \
  --runtime-root "$ESA_RUNTIME" \
  --server-binary "$ESA_RUNTIME/llama_cpp/llama-b11799/llama-server" \
  --n-gpu-layers 99 --ctx-size 16384 \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --threads 6 --batch-size 256 --ubatch-size 128 \
  --max-runtime-seconds 3000 --shutdown-grace-seconds 10 \
  --evidence "$ESA_RUN/server"
```

This uses the same server settings as the successful round. GPU layers 99 requests
offload; verify actual Metal use in `server/stderr.txt`. The d8 launcher supplies
the bounded lifetime and configurable thread/batch settings used for this CSV run.
The [original launcher](run_local_model.py) also supports explicit server/GPU flags,
but retains different defaults (including eight threads); it was separately
smoke-tested, not the launcher used for the timed CSV pass.

Back in the first terminal, check readiness:

```bash
"$ESA_PY_ENV/bin/python" -B - <<'PY'
import time, urllib.error, urllib.request
deadline = time.monotonic() + 60
while True:
    try:
        with urllib.request.urlopen("http://127.0.0.1:18080/health", timeout=5) as response:
            print(response.read().decode())
        break
    except (urllib.error.URLError, TimeoutError):
        if time.monotonic() >= deadline:
            raise SystemExit("Not ready; inspect server logs and stop before task.")
        time.sleep(1)
PY
```

Health should report `ok`. Health alone is not proof that the model can use
tools or produce correct code. This guide's next step makes real model calls.

## 6. Run the guided implementation once

```bash
"$ESA_PY_ENV/bin/python" -B "$ESA_REPO/practice/native_journey/run_observation.py" \
  --preparation "$ESA_PREP" --task "$ESA_RUN/TASK_01.json" \
  --output "$ESA_RUN/attempt_01"
```

Inspect `attempt_01/RECEIPT.json`, raw `stdout.txt`/`stderr.txt`, and
`native-session.json`. A normal recorder or client exit is **not acceptance**.
The receipt reports timeout, duration and out-of-scope changes; actual native
tool events establish whether reads, writes and checks occurred.

Limit this reproduction to **three invocations, each at most 900 seconds**.
The preparation helper's generic protocol permits four invocations; the new
intervention record imposes this stricter three-attempt limit. The recorder
enforces each invocation timeout, not the cumulative attempt count: the operator
must enforce that limit. Steps 12 is a client last-step instruction, not a hard
tool-call count. Stop if the server reaches its lifetime limit; do not run blind
automatic retries.

## 7. Independently verify and snapshot each attempt

Use a new output directory for every review. The review executes the unchanged
supplied checker as well as independent cases and scope checks.

```bash
"$ESA_PY_ENV/bin/python" -B "$ESA_REPO/practice/csv_export/checks/check.py" --candidate "$ESA_PROJECT"
"$ESA_PY_ENV/bin/python" -B "$ESA_REPO/practice/native_journey/independent_review.py" \
  --project "$ESA_PROJECT" --starting-manifest "$ESA_PREP/STARTING_MANIFEST.json" \
  --output "$ESA_RUN/review_01"
"$ESA_PY_ENV/bin/python" -B "$ESA_PROJECT/demo.py" --format csv --actor alice --status open
"$ESA_PY_ENV/bin/python" -B "$ESA_PROJECT/demo.py" --format json --actor alice --status open
cp -R "$ESA_PROJECT" "$ESA_RUN/candidate_after_01"
```

Record each exit code immediately with `echo $?`, and retain stdout/stderr when
running your own audit. Do not let a later successful command mask an earlier
failure. Review the diff against `preparation/starting_project`; keep every
failed snapshot. Do not modify fixtures, checkers, selection or contract.

Expected final results: `PASS_SELECTED_CONTRACT` with seven cases,
`PASS_SELECTED_CONTRACT_AND_SCOPE` with 17 passed and no findings, both demo
exits 0, and no out-of-scope changes. Import/syntax failure can prevent all cases
from running and prevent creation of `REVIEW.json`; absence is not a pass.

## 8. Conditional documents-only continuation

In the successful observation the first candidate passed the seven contract cases
and both demos, but independent review passed only 15/17 because the specification
and plan were absent. **Use this continuation only if your actual results match.**
If code still fails, retain the actual exception and use a new, narrowly guided
task addressing it instead; do not claim the documentation-only case.

The following keeps the same native session and records the passing API hash:

```bash
"$ESA_PY_ENV/bin/python" -B - <<'PY'
import hashlib, json, os
from pathlib import Path
run = Path(os.environ["ESA_RUN"])
project = Path(os.environ["ESA_PROJECT"])
events = []
for line in (run / "attempt_01/stdout.txt").read_text().splitlines():
    try:
        events.append(json.loads(line))
    except ValueError:
        pass
sessions = {e["sessionID"] for e in events if "sessionID" in e}
if len(sessions) != 1:
    raise SystemExit("Cannot identify one native session; inspect events.")
task = json.loads((run / "TASK_01.json").read_text())
prompt = f"""Guided documents-only continuation: independent verification passed
all 7 supplied contract cases and both demos. Independent review passed 15/17;
its ONLY findings are missing spec.md and plan.md. Preserve passing api.py unchanged.
Use actual write tools to create {project}/spec.md and {project}/plan.md.
Name the CSV contract, same actor/status selection, unchanged JSON, ordered
fields/header/escaping/immutability, unsupported formats and literal machine-importer
semantics. Attribute CSV-CONSUMER-01 as fictional. State HTTP, spreadsheet and
deployment limits. Describe the inline csv.writer/io.StringIO design and actual
observed checker results; no invented benefit or human approval.
Run the same exact permitted checker from the original task and report its result.
Distinguish prior missing-document findings from the current result.
No other files need changes. Same 900-second bound and 12-step configuration."""
task["argv"] = task["argv"][:-1] + ["--session", next(iter(sessions)), prompt]
prompt_path = run / "PROMPT_02.txt"
prompt_path.write_text(prompt)
task["prompt_reference"] = str(prompt_path)
task["prompt_sha256"] = hashlib.sha256(prompt.encode()).hexdigest()
(run / "TASK_02.json").write_text(json.dumps(task, indent=2) + "\n")
(run / "API_BEFORE_DOCS.sha256").write_text(hashlib.sha256((project / "api.py").read_bytes()).hexdigest() + "\n")
PY
"$ESA_PY_ENV/bin/python" -B "$ESA_REPO/practice/native_journey/run_observation.py" \
  --preparation "$ESA_PREP" --task "$ESA_RUN/TASK_02.json" \
  --output "$ESA_RUN/attempt_02"
```

Repeat **all** section 7 checks with a new `review_02` and
`candidate_after_02` destination. Compare the final API hash with the stored
hash and inspect `attempt_02/RECEIPT.json`: the observed continuation changed
only the two documents. Read the documents yourself; the 17-case reviewer tests
nonempty existence, not complete prose accuracy. The extra stale-finding warning
above is an editorial improvement to the reproduction prompt, not part of the
original observed prompt.

If the checks pass, stop. If they fail, preserve them and respect the remaining
attempt budget. A stronger prompt, manual patch or model change must be disclosed;
do not relabel an assisted or edited solution an unaided model success.

## 9. Stop the owned server and retain the evidence

In the server terminal press Ctrl-C. The launcher terminates its own server,
waits for its grace period, and records `FINISH.json`. If using another terminal,
identify the launcher's PID from this run's `START.json`, verify that PID still
belongs to this launcher, then send SIGTERM to that exact process. Do not use
broad process-name kill commands.

Require a finish receipt; inspect exit code and shutdown reason. Verify the
recorded server/launcher processes are gone and port 18080 is clear. The successful
run exited 0 after SIGTERM. Darwin maximum RSS is reported by the OS in bytes;
the updated receipts retain raw units and normalized KiB. Earlier receipts with
only the mislabeled KiB field must not be retroactively rewritten.

Keep the whole `ESA_RUN` outside Git: preparation and original/effective config,
prompts/tasks/interventions, starting manifest, each candidate snapshot, raw native
events/session exports, reviews/demo outputs, runtime identities, server logs and
finish receipt. Paths in retained commands describe where they ran; relocating a
packet does not make those paths automatically replayable. Create a SHA-256 file
inventory and verify a durable copy before deleting temporary evidence. Never
include credentials in a shared packet.

The shipped starter remains intentionally incomplete. Do not copy a passing
candidate over it. Review the candidate independently and decide explicitly how
you want to use it.

## 10. What was actually observed, and where to review it

The audit report distinguishes the original emulated timeout, failed native
retries, and the final successful guided run:
[execution report](../../validation/EXAMPLE_TEST_REPORT.md#successful-fresh-guided-csv-retry).

On the original workstation the durable successful packet is
`/Users/enricopapalini/local_repos/esa_ai_native_runtime_darwin_01/validation_evidence_guided_fresh/`.
It contains `SUMMARY.json`, `project/`, per-attempt receipts, original prompts,
effective configuration, candidate snapshots, reviews and a hash inventory.
These machine-local artifacts are not distributed in Git.

Only the final guided round achieved the 7+17 pass. Earlier failed candidates
were retained separately, not overwritten. No manual candidate implementation,
checker changes or reference-solution patch was used. Read permissions were
explicitly extended to the actual API dependency and contract. Final code was
also checked using the official repository's independent reviewer.

For the wider non-model regression checks, optional tool suites, Linux-only
clock test and remaining live gaps, follow the commands and limits in the
[execution report](../../validation/EXAMPLE_TEST_REPORT.md#reproduce-the-main-local-checks).
Do not interpret this one CSV pass as coverage of every SDD/MCP/model-driven path.

### Troubleshooting

| Symptom | Check / action |
| --- | --- |
| Wrong Python in native bash tool | Put the venv bin first on PATH **before preparation**; inspect the retained environment |
| Missing/non-executable server or model | Verify paths and hashes; launcher refuses before creating evidence |
| Very slow first prompt on Apple Silicon | Check native ARM64 binary and actual Metal offload; do not just extend deadlines |
| Linux binary reports missing libgomp | Install OpenMP in that Linux environment, not on the macOS host |
| Denied read despite alternate task environment | Change/capture the actual preparation config; the recorder ignores alternate task environment references |
| Client exits 0 but candidate fails | Inspect API/imports and unchanged independent checks; client exit is not acceptance |
| Undefined helper/deleted API/duplicate edits | Preserve failure; use fresh starter and focused API-preserving guidance |
| CSV escaping failures | Use standard CSV serialization; check commas, quotes, CR/LF and Unicode round trips |
| Only missing specification/plan | Freeze passing API, request documents only, rerun all checks |
| Existing output directory | Choose a new attempt/run name; do not erase previous evidence |
| Model task reaches timeout | Preserve receipt and partial candidate, stop within budget, diagnose before retry |
