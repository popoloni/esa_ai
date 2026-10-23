# Proposed portable d8 native route

This is future-recipe text for integration after the actual journey is reviewed.
It makes no generation or acceptance claim. Preserve the earlier helper names
and their historical observations. The two new helpers are
`practice/native_client/configure_sdd_d8.py` and
`practice/native_client/run_local_model_d8.py`.

## Fresh paths and unchanged inputs

Use absolute paths for `ESA_COMPANION` (the companion root), `ESA_RUNTIME`
(the pinned installed toolchain), and `ESA_PACKET` (the earlier setup/configuration
packet). Install the versions from the native-client setup before this procedure:
OpenCode 1.19.3, Spec Kit 1.2.2, llama.cpp b11799 and the pinned Qwen3-4B GGUF.
The earlier Chapter 1 model run is not required. Retain installation evidence.

Choose a new writable run root and new evidence/state directories. Keep the
project outside a Git worktree because this helper verifies that permission
path basis. The following variables are examples of directory roles, not
historical paths to reuse:

```bash
export ESA_SDD_RUN_ROOT="/absolute/path/to/new-sdd-run"
export ESA_SDD_WORK="$ESA_SDD_RUN_ROOT/native_sdd_01"
export ESA_SDD_PACKET="$ESA_SDD_RUN_ROOT/evidence"
export ESA_SDD_STATE="$ESA_SDD_RUN_ROOT/client-state"
export PATH="$ESA_RUNTIME/opencode/node_modules/.bin:$ESA_RUNTIME/sdd_venv/bin:$PATH"
mkdir "$ESA_SDD_RUN_ROOT"
cd "$ESA_SDD_RUN_ROOT"
specify init native_sdd_01 --integration opencode --script py --non-interactive
```

Copy the nine fixed JSON inputs and unchanged router, then retain the original
installed scaffold before configuration. This supplies the authored reference
contract in `inputs/specification.json`; it does not provide an earlier generated
Markdown specification, exercise answers, evaluation reviews or owner responses.

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
shutil.copytree(work, packet / 'initial_tree')
manifest = {p.relative_to(work).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(work.rglob('*')) if p.is_file()}
(packet / 'INITIAL_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
PY
cd "$ESA_COMPANION"
```

## Start a separately recorded server and prepare the client

Run the server in a separate terminal after stopping any prior owned server.
The launcher makes no model request. This command explicitly selects 24,576
context tokens, f16 K/V, 256 batch, 128 microbatch and eight threads. The launcher
also uses `--no-repack`, `--no-warmup`, one slot, disabled context shifting and
no server-side agent tools. Its initial 22,528 default remains in the source;
this recipe passes 24,576 explicitly.

```bash
python3 -B practice/native_client/run_local_model_d8.py \
  --runtime-root "$ESA_RUNTIME" --evidence "$ESA_SDD_PACKET/server_01" \
  --ctx-size 24576 --cache-type-k f16 --cache-type-v f16 \
  --batch-size 256 --ubatch-size 128 --threads 8 \
  --max-runtime-seconds 7200 --shutdown-grace-seconds 30
```

Retain actual health, model/binary identity, context, memory and process checks.
A healthy start does not establish completion or sustained memory headroom.
The remaining server lifetime must cover the new 5,400-second client bound and
cleanup; starting a replacement is a separate recorded lifecycle.

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

This helper prepares a task and performs bounded version/configuration/agent
diagnostics. It makes no inference request. Inspect every check in
`CONFIGURATION_NOTES.json`, including discovery of the unchanged full
`speckit.specify` and `speckit.clarify` command bodies.

The packet includes all nine original JSON values, the complete router, both
complete active templates and the unratified constitution. Only JSON whitespace
changes; line wrapping avoids the pinned native reader's per-line clipping.
The task uses an `@absolute-file` reference in the unchanged native command,
so the client preloads the full packet before inference. `run --command --file`
is not an equivalent attachment route in this pinned client.

Later model reads are limited to the three output files. The source bundle,
individual sources and templates are unavailable to repeated model read calls;
their complete content is already attached. The exact bash allowlist has no
`cat` command. Writes remain limited to the feature marker, specification and
requirements checklist. These are client permissions, not OS containment.

The custom model declares `temperature: true` and the agent requests 0.2.
Preserve actual effective model capability and the observed request/sampler
when reporting a run. The client output limit is 3,072 per response. The
recorded server exposed a default of -1 despite its `--n-predict` argument, so
do not claim a separately enforced server output cap from that argument.

## Budget, preserve and invoke

Retain the complete prepared project in a new `starting_tree` snapshot after
configuration. Preserve the initial scaffold separately. Measure the complete
native command with both argument expansions and CLI quoting, the actual
native attachment text, and the chat wrapper using the pinned tokenizer.
Budget system/tools, cumulative prior output/tool history and the current
response. The historical candidate03 reserved 3,072 + 4,096 + 3,072 tokens
respectively; these are explicit reserves, not a guarantee for changed inputs
or repeated generated-output reads. The helper does not measure this budget.
Preserve overflow, refusals or timeouts instead of dropping sources.

After the actual full-input, memory and permission checks and a checkpoint,
start a new generation session from the prepared task. Never reuse a noReply
preparation session. Keep one model task active on this one-slot server.

```bash
python3 -B validation/observe_native.py capture \
  --spec "$ESA_SDD_PACKET/CLIENT_TASK_01.json" \
  --output "$ESA_SDD_PACKET/attempt_01"
```

The model is configured for 24,576 context tokens and 3,072 output tokens per
response, with explicit 1,500-second overall and header deadlines. The fixed
5,400-second outer capture timeout is the subprocess bound. In the pinned
OpenCode loop, `agent.steps: 12` adds a last-step instruction while tools remain
available; it is not a mechanical limit on tool calls. Record setup work, failed attempts and all
interventions. Export the observed native session to a regular file, preserve
first write/edit inputs and final file bytes, and distinguish a template copy
from generated feature content. An exit code alone does not prove completion.

Review actual output against all five requirements, all eight scenarios, policy
identity and the separate human payment boundary. Keep all three supplied owner
questions unresolved and benefit unvalidated. Retain actual clarification or
an explicit deferral; a model recommendation is not an owner answer. Stop before
planning or implementation. A later clarify invocation is a separately declared
step only if the generated specification exists and further clarification is
needed. No generated artifact or owner answer is supplied by this recipe.
