# Run and review a native Spec Kit journey

This is the current route for the 22 October d8 observation. It uses the full
installed Spec Kit 1.2.2 command in OpenCode 1.19.3 with the pinned local model
stack from the [native-client setup](../native_client/README.md). The
[observed packet](observed_native_20261022_d8/README.md) retains every failed
attempt, the first defective write and the later useful native response.

The original R08 tutorial scope is now observed and independently reviewed.
The useful specification is a **native response artifact**, not the file saved
in the native project. The actual saved file is rejected, the checklist and
feature metadata were not created, and the response’s claim of three artifacts
is false. The [reader specification](observed_native_20261022_d8/editorial/reader_specification.md)
is an explicitly attributed editorial extraction with an exact diff. Human
requirements acceptance, owner answers and implementation readiness remain
absent. A separate speckit.clarify invocation and interactive owner dialogue
were not observed.

## 1. Prepare a fresh installed scaffold

Complete native-client dependency setup first. In that guide, ESA_COMPANION is
the unchanged companion root, ESA_RUNTIME is the installed pinned runtime and
ESA_PACKET is its local-client configuration evidence. The Chapter 1 model run
is not a prerequisite. Install the recorded Spec Kit environment if it is not
already present, preserving actual dependency versions and output:

```bash
uv --cache-dir "$ESA_RUNTIME/python-cache" venv "$ESA_RUNTIME/sdd_venv"
uv --cache-dir "$ESA_RUNTIME/python-cache" pip install \
  --python "$ESA_RUNTIME/sdd_venv/bin/python" \
  -r "$ESA_COMPANION/practice/sdd/evidence/toolchain/python_requirements.lock.txt"
```

Choose unused paths. The prepared permission recipe is scoped to the observed
non-Git directory; the helper stops if it finds a Git worktree. Do not erase an
earlier attempt or change repository identity to bypass that check.

```bash
export PATH="$ESA_RUNTIME/opencode/node_modules/.bin:$ESA_RUNTIME/sdd_venv/bin:$PATH"
export ESA_SDD_WORK="$ESA_RUNTIME/native_sdd_d8_01"
export ESA_SDD_PACKET="$ESA_RUNTIME/sdd_evidence_d8_01"
export ESA_SDD_STATE="$ESA_RUNTIME/sdd_client_state_d8_01"
cd "$ESA_RUNTIME"
specify init native_sdd_d8_01 --integration opencode --script py --non-interactive
```

Copy the fixed inputs and unchanged router, then retain the installed starting
tree before configuration:

```bash
python3 - <<'PY'
import hashlib, json, os, shutil
from pathlib import Path
companion = Path(os.environ['ESA_COMPANION'])
work = Path(os.environ['ESA_SDD_WORK'])
packet = Path(os.environ['ESA_SDD_PACKET'])
shutil.copytree(companion / 'practice/sdd/shared', work / 'inputs')
(work / 'source/treasury').mkdir(parents=True)
shutil.copy2(companion / 'repo/src/treasury/routing.py',
             work / 'source/treasury/routing.py')
packet.mkdir(parents=True, exist_ok=False)
shutil.copytree(work, packet / 'starting_tree')
manifest = {p.relative_to(work).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(work.rglob('*')) if p.is_file()}
(packet / 'STARTING_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
PY
cd "$ESA_COMPANION"
```

The supplied inputs/specification.json is the authored reference contract. It
already contains the five requirements and eight expected cases. This is a
disclosed projection exercise, not blind requirements discovery. Do not supply
earlier generated Markdown answers or owner responses as if they were new
observations. Keep the original installed command bodies and source values.

## 2. Prepare and inspect the actual client configuration

The new helper names preserve the earlier d7 helpers and their historical
configurations. The following explicit limits reproduce the corrected d8
candidate’s configuration after path normalization:

```bash
python3 -B practice/native_client/configure_sdd_d8.py \
  --project "$ESA_SDD_WORK" --evidence "$ESA_SDD_PACKET" \
  --state "$ESA_SDD_STATE" \
  --opencode "$ESA_RUNTIME/opencode/node_modules/.bin/opencode" \
  --specify "$ESA_RUNTIME/sdd_venv/bin/specify" \
  --base-config "$ESA_PACKET/configuration/OPENCODE_CONFIG.json" \
  --base-environment "$ESA_PACKET/configuration/ENVIRONMENT.json" \
  --compact-context --context-tokens 24576 --output-tokens 3072 \
  --provider-timeout-ms 1500000 --outer-timeout-seconds 5400
```

This prepares files and runs real version, effective-configuration and
effective-agent diagnostics; it does not invoke the model. Inspect
CONFIGURATION_NOTES.json. The complete original speckit.specify and
speckit.clarify bodies must be discovered without an injected replacement, all
checks must pass, and the original project files must remain unchanged.

The helper creates a complete 13-source Markdown packet: nine fixed JSONs,
the router, both active templates and the unratified constitution. It preserves
all JSON values and all other source bytes. JSON whitespace is wrapped so no
line reaches the pinned client’s 2,000-unit line limit. The helper also checks
the native line-count and byte limits; it refuses a known oversized attachment.

The prepared command passes an **absolute @file reference**. In pinned OpenCode
1.19.3, the command path expands that reference into a native attachment before
inference. The CLI’s ordinary --file argument is not passed through its
--command branch, so it is not an equivalent way to provide these inputs.
The retained [attachment preflight](observed_native_20261022_d8/recorded/invocation_03/PREFLIGHT_SUMMARY_03.json)
verifies the full native read without inference in a separate noReply session.
That preparation session was never reused for generation.

After attachment, model reads are allowed only for the three generated output
paths. Duplicate source, template and bundle reads are denied; the shell
allowlist also excludes a duplicate bundle read. Writes are restricted to the
feature metadata, selected spec and its checklist. Inspect the effective
permissions, including the client’s own tool-output exception. These are
client-level scope controls, not OS containment.

Temperature capability is explicitly enabled so the agent’s intended 0.2 is
actually sent. The first d8 attempt lacked that capability and used an observed
0.8; its configuration remains unchanged. Automatic compaction is disabled and
the prepared session has an explicit title. Provider overall timeout and header
timeout are separate settings, both explicitly 1,500,000 milliseconds here.
The 12-step setting triggers a last-step instruction; it does not mechanically
cap tool calls. The 5,400-second capture timeout is the outer subprocess bound.

The [actual portable-helper reproduction](observed_native_20261022_d8/reproduction/actual_reproduction_01/REPRODUCTION_REVIEW.json)
ran this helper against a separate 49-file project and isolated state after the
server stopped. Real diagnostics passed, the full command/argv/configuration
matched the observed candidate after declared path substitutions, and every
source body and the regenerated bundle matched. No simulated diagnostic or
model call was used. This verifies preparation, not future generation success.

## 3. Check the server and complete context budget

Start a fresh owned server in another terminal, with a new evidence directory.
Keep any earlier server lifecycle intact and stop that owned process before
reusing the loopback port:

```bash
python3 -B practice/native_client/run_local_model_d8.py \
  --runtime-root "$ESA_RUNTIME" --evidence "$ESA_RUNTIME/sdd_server_d8_01" \
  --ctx-size 24576 --cache-type-k f16 --cache-type-v f16 \
  --batch-size 256 --ubatch-size 128 --threads 8 \
  --max-runtime-seconds 7200 --shutdown-grace-seconds 30
```

The launcher’s retained argv also sets no-repack, no-warmup, one CPU slot,
disabled reasoning and no automatic context shift. The
[closed runtime packet](../native_client/setup/runtime_d8/README.md) records the
actual startup, memory and shutdown evidence. Verify current health, actual
context, binary/model identity and available memory before a model request.
A healthy startup does not guarantee sustained headroom or timely completion.
The observed server’s props reported an unlimited default despite its requested
n-predict argument. The configured client cap follows the
[pinned serialization source chain](observed_native_20261022_d8/recorded/input_budget/CLIENT_OUTPUT_CAP_SOURCE_BINDING.json);
an actual provider HTTP request body was not captured. Keep that source-based
expectation distinct from an observed wire field, and do not claim a separately
proven server-enforced cap.

Measure the full expanded command and the actual attached content with the
pinned model’s tokenizer. Include both command-argument expansions, native
wrapping, system/tool instructions, cumulative history/tool results and the
next output. The helper does not make that measurement. Retain the exact
read-only tokenizer/template requests and responses. For the recorded guarded
candidate, the measured user wrapper was 13,025 tokens; 3,072 for the native
envelope, 4,096 for history and 3,072 for output made a 23,265-token preparation
budget within 24,576. The first actual native request was 15,872 tokens, so the
measured envelope overhead fit that reserve. These values belong to the
recorded files and paths, not every future setup.

The earlier 22,528 candidate failed the conservative budget and was retained as
a rejected preparation. A changed path, source or history needs a new budget.
Do not shorten the framework instructions or silently drop source fields to
make it fit. Confirm the owned server’s remaining lifetime exceeds the declared
client bound with cleanup margin. Use one inference request stream at a time.

## 4. Capture one declared invocation and review what it actually did

Retain the final prepared tree and input/configuration identities. Record a new
account start and execute the exact prepared task into a fresh capture folder:

```bash
python3 -B validation/observe_native.py capture \
  --spec "$ESA_SDD_PACKET/CLIENT_TASK_01.json" \
  --output "$ESA_SDD_PACKET/attempt_01"
```

The task invokes the real installed speckit.specify command. It does not supply
an authored generated artifact or a replacement command. Preserve each first
completed write/edit payload and separately observed file bytes, because native
formatters can change what reaches disk. Do not export the active client
database. After the terminal receipt and actual native process exit, use the
native-client guide’s regular-file export procedure, verify the actual session
identity and freeze the complete final tree/diff. Exit zero alone is not task
acceptance.

The recorded d8 correction used two explicitly retained same-session requests,
not automatic retries disguised as a new trial. The first continuation kept
the 3,072 response cap and declared a 3,600-second outer bound; it timed out
without artifact content. The second changed only the output limit to 1,536,
declared a 2,400-second outer bound and requested a compact spec-only write.
The one-write request and content-length target were guidance, while the
existing permissions still allowed the original three output paths. All source
exposure and original native command history remained available. Historical
session IDs refer to the original database; use and retain your own actual
identity before any separately declared continuation.

The final native response contained all requirements/cases and left all three
owner questions unanswered, then normally stopped. The useful body was not
saved. Review native text, actual files and process status as separate facts.
An editorial extraction can make genuine response content easier to read, but
must retain the raw response, exact diff and attribution; it cannot be relabeled
as a native file write or used to conceal the failed candidate.

## 5. Keep the human decision boundary explicit

Trace every requirement, source and scenario to the fixed inputs. In particular,
EUR 5,000 requires HUMAN_REVIEW with AT_OR_ABOVE_LIMIT and BR-001/v1. Invalid
and non-positive inputs remain rejected. No route is payment authorization.
Benefit remains HYPOTHESIS_NOT_VALIDATED and the constitution remains
unratified. Inspect unsupported completion statements as well as omitted cases.

The actual unanswered questions concern operator vocabulary, accidental
payment approval and benefit measurement in a pilot. If a command presents
those questions and stops without answers, retain and review that reached
boundary. Do not supply an owner response or claim planning readiness simply
because content exists. The observed d8 response met the original bounded
question-stop requirement without a separate clarify invocation. A future
speckit.clarify phase requires its own exact artifact, full command context,
budget and attributable answers or documented stop; it is not retroactively
claimed here.

OpenSpec remains the unobserved native contrast. One observed primary route
satisfies this tutorial; a measured paired comparison would require the second
observed route. The [earlier route](NATIVE_ROUTE.md) and its d7 timeout records
remain dated history, not a statement that current native generation is absent.
