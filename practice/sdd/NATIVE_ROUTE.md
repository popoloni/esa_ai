# Earlier d7 native preparation and observation

**Historical scope:** this page retains the earlier d7 recipe and its dated
incomplete observations. Use [the current d8 native route](NATIVE_ROUTE_D8.md)
for the revised preparation and [current observed packet](observed_native_20261022_d8/README.md)
for actual native response generation, the failed save and the independently
reviewed unanswered-question stop. The d7 raw evidence and manifests remain
unchanged. The step setting mentioned below is a last-step instruction in the
pinned client, not a mechanical tool-call bound; the outer capture timeout is
the subprocess bound.

This optional route uses Spec Kit 1.2.2 and OpenCode 1.19.3 with the same local
model stack as the [native-client exercise](../native_client/README.md). It
asks the real `speckit.specify` command to project the fixed Treasury inputs
into its own specification and quality checklist. The generated result still
requires review. The three unanswered operator and benefit questions remain
unanswered until an appropriate owner supplies evidence or a justified decision.

Keep the authored comparison fixtures and the external ChatGPT generation
separate from this native observation. One observed primary route is sufficient
for the tutorial. This procedure provides no measured framework ranking.

The first native attempt retained a provider timeout before any specification
or checklist was generated. Its 600-second overall timeout did not override
OpenCode's separate 300-second header deadline. An automatic session-title
request also competed for the single model slot. The recovery recipe below
sets both deadlines explicitly, names the session, and budgets the complete
command and inputs. The original attempt remains an actual failed observation;
see the [pinned client-source diagnosis](../native_client/setup/runtime_d7/diagnosis/README.md).
The [22 October native packet](observed_native_20261022/README.md) retains the
actual attempts, original responses, follow-up guidance and reached boundaries.

The repaired fresh attempt returned a short name and stopped without using a
tool. Its final, separately bounded same-session continuation completed the full
packet read, then reached the 1,800-second outer limit without generating any of
the three requested files. This remains an incomplete native generation journey.
The recipe below prepares a fresh attempt; it does not promise completion.

## 1. Prepare the dependencies and a fresh project

Complete native-client setup through configuration, so `ESA_COMPANION`,
`ESA_RUNTIME` and `ESA_PACKET` identify your unchanged companion, installed
runtime and Chapter 1 evidence packet. The Chapter 1 model run is not a
prerequisite for this setup. Preserve the actual versions and dependency output.

From the unchanged companion root, install the recorded Python dependency set
in a new environment. Use the configured registry/proxy and trusted TLS setup:

```bash
uv --cache-dir "$ESA_RUNTIME/python-cache" venv "$ESA_RUNTIME/sdd_venv"
uv --cache-dir "$ESA_RUNTIME/python-cache" pip install \
  --python "$ESA_RUNTIME/sdd_venv/bin/python" \
  -r practice/sdd/evidence/toolchain/python_requirements.lock.txt

export PATH="$ESA_RUNTIME/opencode/node_modules/.bin:$ESA_RUNTIME/sdd_venv/bin:$PATH"
export ESA_SDD_WORK="$ESA_RUNTIME/native_sdd_01"
export ESA_SDD_PACKET="$(dirname "$ESA_PACKET")/esa_sdd_evidence_01"
export ESA_SDD_STATE="$ESA_RUNTIME/sdd_client_state_01"
cd "$ESA_RUNTIME"
specify init native_sdd_01 --integration opencode --script py --non-interactive
```

These paths must be unused. The prepared observation uses a non-Git directory;
the configuration helper stops if it detects a Git worktree because the client's
permission paths would need separate verification. Do not erase an existing
attempt or initialize a Git repository to hide that diagnostic.

Copy the fixed inputs and the unchanged router. The supplied
`inputs/specification.json` is the authored reference contract and is disclosed
input. This copies no earlier generated specification, plan or task list,
no before/after Markdown exercise answers, and no owner response:

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

The fixed inputs already contain contract and scenario decisions from the
teaching case. This is a disclosed projection exercise. It is not blind
requirements discovery or evidence that real operators benefit from the feature.

This SDD recovery uses a different declared server configuration from the
Chapter 1 observation: a 24,576-token context and `q4_0` key/value caches. Stop
your own idle default launcher cleanly first, retain its finish receipt, and
start a fresh server record in a separate terminal:

```bash
python3 -B practice/native_client/run_local_model.py \
  --runtime-root "$ESA_RUNTIME" --evidence "$ESA_RUNTIME/sdd_server_01" \
  --ctx-size 24576 --cache-type-k q4_0 --cache-type-v q4_0
```

Check actual health, `/props` context, process identity and available memory
before submitting a model request. This numerical/cache change is disclosed;
it is not a performance or quality comparison. A successful load alone does
not guarantee that the complete journey will fit memory or finish in time.

## 2. Inspect the native command and permissions

```bash
python3 -B practice/native_client/configure_sdd.py \
  --project "$ESA_SDD_WORK" --evidence "$ESA_SDD_PACKET" \
  --state "$ESA_SDD_STATE" \
  --opencode "$ESA_RUNTIME/opencode/node_modules/.bin/opencode" \
  --specify "$ESA_RUNTIME/sdd_venv/bin/specify" \
  --base-config "$ESA_PACKET/configuration/OPENCODE_CONFIG.json" \
  --base-environment "$ESA_PACKET/configuration/ENVIRONMENT.json" \
  --compact-context --context-tokens 24576 --provider-timeout-ms 900000
```

This command prepares configuration and runs version/configuration diagnostics;
it makes no model request. Inspect `CONFIGURATION_NOTES.json`. All listed checks
must pass, including discovery of the complete original `speckit.specify` and
`speckit.clarify` command bodies. A command name appearing in a menu alone does
not establish that its instructions were retained or executed.

`--compact-context` creates one Markdown packet containing all nine fixed JSON
sources, the complete router, both active templates and the unratified
constitution. It verifies the original input hashes, compacts JSON whitespace
only, and verifies that every parsed JSON value is identical. Other source
contents are reproduced completely. Original files remain present; the notes
retain the packet identity and every source hash. The complete upstream command
is unchanged. Short task arguments point to this packet because the native
command expands its argument placeholder twice.

The helper restricts writes to `.specify/feature.json`, the selected `spec.md`
and its requirements checklist. It permits a single exact
`cat inputs/NATIVE_CONTEXT_BUNDLE.md` input read through the shell tool and a
small command allowlist; the general read tool is disabled in this mode to avoid
duplicate input delivery. It disables automatic compaction and other providers.
These are client controls, not OS containment. Read the complete effective
permissions, including the client's internal tool-output-directory exception.

Inspect `TASK_PROMPT_01.txt`. The threshold, equality case, rejection semantics
and `payment_authorized=false` must remain intact. The source constitution is
an unratified upstream template, not adopted project governance. Planning and
implementation are outside this attempt's scope.

Retain the actual prepared tree after diagnostics as well as the original
scaffold. This includes the input packet and any separately identified client
infrastructure additions, while preserving the initial snapshot:

```bash
python3 - <<'PY'
import hashlib, json, os, shutil
from pathlib import Path
work = Path(os.environ['ESA_SDD_WORK'])
packet = Path(os.environ['ESA_SDD_PACKET'])
shutil.copytree(work, packet / 'prepared_tree')
manifest = {p.relative_to(work).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(work.rglob('*')) if p.is_file()}
(packet / 'PREPARED_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
PY
```

## 3. Run the real framework command once

Keep the local model server running. Do not run another model task concurrently
in the one-slot CPU configuration. Before capture, check the complete expanded
command and packet against the actual backend context. The configuration helper
explicitly does **not** measure tokens. The retained recovery preflight and
`observed_native_20261022/recovery_01/TOKENIZER_MEASUREMENTS.json` show the
actual tokenizer responses: 4,452 command tokens and 6,698 packet tokens, plus
explicit reserves of 4,096 for system/tools/envelopes, 8,192 for aggregate
assistant output/history and 512 for other tool results. Those numbers belong
to the recorded paths and prompt. Measure a changed prompt or packet again;
include both expansions of the full command argument and native CLI quoting.
Stop preparation if the full budget does not fit. Preserve the health, context
and resource checks; do not silently trim instructions to make it fit.

Record your preparation time and start a new attempt, then execute the exact
prepared task:

```bash
python3 -B validation/observe_native.py capture \
  --spec "$ESA_SDD_PACKET/CLIENT_TASK_01.json" \
  --output "$ESA_SDD_PACKET/attempt_01"
```

The task invokes `opencode run --command speckit.specify`; it does not substitute
an authored template or shortened command. The declared bounds are 12 agent
steps, a 24,576-token context, 2,048 output tokens per response, explicit
900-second overall and header deadlines per request, and a 1,200-second outer
capture limit. They describe the
attempt, not a completion guarantee. Retain an overflow, timeout, refusal or
incomplete output as an actual result.

Export the observed session to a regular file using the native-client guide's
export procedure, with this packet's `CLIENT_TASK_01.json` and `attempt_01` paths.
Keep the first spec/checklist bytes and the actual diff before making a correction.
The process exit status and the requested task outcome are different facts.

The recorded follow-up used `opencode run --session` with the observed session
identity and an explicitly retained execution request. It kept the complete
original command and first response in history, used separate 1,500-second
provider deadlines and a fixed 1,800-second outer bound, and made no later
attempt. Its preparation and exact appended prompt are in
`observed_native_20261022/guided_continuation_01/`. Historical session IDs depend
on the original client database; a reader must retain their own actual session
identity and history before any separately declared continuation.

## 4. Review and stop at the reached boundary

Trace all five requirements and all eight cases to the fixed input. Check that
5,000 requires human review, invalid amounts are rejected, the source policy
identity remains correct, and an explanation never authorizes a payment.
Review the checklist for unsupported ticks, invented outcomes, missing cases
and assumed owner answers. The fixture checker's exact-wording pass is not a
substitute for reviewing a newly generated document.

Keep these questions explicit:

1. Which explanation vocabulary do real operators understand?
2. Does the interface accidentally induce payment approval?
3. How will actual user benefit be measured in a pilot?

If `specify` asks these questions and waits, retain that stop. If it never creates
a usable spec, retain its failure and do not plant an authored spec to unlock
another phase. If a usable spec exists and further clarification is warranted,
prepare a separately recorded invocation of the discovered `speckit.clarify`
command, scoped to that exact spec. It asks material questions and needs actual
attributable answers or a documented deferral. Do not substitute a model's
recommendation for an owner's response or claim a planning gate passed merely
because files exist.
