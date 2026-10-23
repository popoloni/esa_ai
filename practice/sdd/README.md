# Same Treasury task, two SDD workflows

[Home](../../README.md) · [Practice catalogue](../README.md) · [Chapter routes](../../navigation/CHAPTER_ROUTES.md)

For the current installed-client route, use [Run and review a native Spec Kit
journey](NATIVE_ROUTE_D8.md). The [d8 native packet](observed_native_20261022_d8/README.md)
retains the useful generated response, the rejected file actually written, all
earlier failures and the independently assessed unanswered-question stop. Its
[reader specification](observed_native_20261022_d8/editorial/reader_specification.md)
is a separately attributed editorial extraction, not a native-persisted file.
Owner answers and human requirements acceptance remain absent.

This Chapter 4 practice uses **Spec Kit as the primary artifact journey and
OpenSpec as the contrast**. Both receive the same explanation-only Treasury
intent, five requirements, eight expected cases and pending human-review state.
It connects Chapter 3's discovery decision to Chapter 5's design question.

## Start here

Run from the cumulative `companion/` directory, using Python 3.12 for this recorded
run. The exercise itself uses only the standard library; no account, model or
framework installation is needed to inspect and repair the supplied artifacts.

```bash
python3 practice/sdd/exercise.py
python3 practice/sdd/check.py --artifacts practice/sdd/work
```

The second command should exit **1**, with exactly one finding per flow:

```text
speckit: FAIL (1 finding(s))
  MISSING_CASE:SC-EXPL-002
openspec: FAIL (1 finding(s))
  MISSING_CASE:SC-EXPL-002
Human requirements approval: PENDING. Named-agent generation: NOT_RUN.
```

Read the unchanged example for exactly EUR 5000 in `shared/case_oracle.json`.
Then add that scenario to these two files in your new working copy:

- `work/speckit/spec.md`
- `work/openspec/openspec/changes/explain-treasury/specs/explanation/spec.md`

Run the checker again. The expected repaired result is PASS for both flows;
human approval is still pending. The `ORIGIN.json` files describe where the
initial exercise artifacts came from, not an approval or a live client session.
Do not change those provenance records to claim either.

To inspect the retained worked answer after your attempt:

```bash
python3 practice/sdd/check.py --artifacts practice/sdd/fixtures/after
python3 practice/sdd/check.py --artifacts practice/sdd/fixtures/after --json
```

The two repair diffs and `review/correction_record.json` explain the change.
For another attempt, retain your old directory and choose a fresh destination,
for example `python3 practice/sdd/exercise.py --out /tmp/sdd-second-attempt`.
The copier refuses to overwrite an existing attempt. It does not reset or repair
the cumulative lab's separate CP03/CP04/CP05 candidates.

## What was actually run

The observed local runs on 20 October 2026 are deliberately separated:

| Layer | Actual operation | What its result establishes |
| --- | --- | --- |
| Spec Kit 1.2.2 CLI | Local init for the Codex integration; bundled Python helpers create blank feature/spec and plan scaffolds and return a task template. | These CLI/template operations worked in the recorded Linux environment. They did not run Codex or generate the Treasury requirements. |
| OpenSpec 1.14.1 CLI | Local init for the Codex integration, new change metadata and artifact status. | The CLI created the structure and reported file/dependency state. No coding-agent session was launched. |
| OpenSpec strict validation | `validate explain-treasury --type change --strict --json --no-interactive`, against both authored specimens. | Both before and after specimens passed this tool's structural rules in the observed run. |
| Independent book checker | Read the actual Markdown against fixed source/owner metadata, requirement wording and all eight selected cases. | Both before specimens fail for missing SC-EXPL-002; both repaired specimens pass those checks. |
| Fresh-copy repair | Create a new editable attempt, observe failure, insert one missing scenario into each specification, rerun. | Exactly two spec files changed and the case-level result changed from FAIL to PASS. |
| Checker negative controls | Fourteen local `unittest` cases. | Selected wrong outputs, forged authority, provenance changes, duplicate cases and substitutions are detected. |

The populated spec/plan/tasks and proposal/design documents are **authored
teaching specimens**. They were not produced by Spec Kit's or OpenSpec's agent
skills. The missing equality case was deliberately seeded in both. It is not
evidence that either framework or an LLM made that mistake. No framework winner,
generation-quality score, time saving or human comprehension result follows.

Spec Kit's template helper returning a task template is not a generated
Treasury task list. Likewise, OpenSpec's `status` reporting all four artifact
files `done` is not human requirements approval. The supplied task documents
remain explicitly blocked pending that review.

## Follow the two artifact journeys

| Review question | Spec Kit exercise | OpenSpec exercise |
| --- | --- | --- |
| What is the proposed feature? | `spec.md` carries behavior, source authority and examples. | `proposal.md` gives the change reason; the explanation capability's delta spec carries behavior and examples. |
| What remains unchanged? | Review boundary in the feature spec; source links and five excluded actions. | No existing routing capability is modified; the added capability is presentation. The same exclusions remain in the delta. |
| How might it be built? | Candidate `plan.md`. | Candidate `design.md`. |
| What work is proposed? | `tasks.md` traces all five requirements and names the equality case. | The same task obligations in the change directory. |
| Who can accept it? | Real product/policy review is absent and pending. | The same absent/pending decision; file completion does not supply it. |

Notice the useful inconsistency in the before set: task T02 asks for the equality
case, but the behavioral spec omits it. An artifact inventory alone will not
resolve that mismatch. The fixed external case oracle does. Both incomplete
specs also agree with each other; their agreement is insufficient.

## Fixed inputs and allowed edits

`shared/` contains byte-for-byte copies of the existing CP04 reference contract,
case oracle, corrected discovery handoff, discovery assessment and five source
records. `shared/INPUT_MANIFEST.json` binds them to their unchanged cumulative
companion sources. The checker also binds that manifest to a published digest.

In this exercise, "fixed" means **not editable as part of the comparison**. Hash
checks detect selected changes; an agent with access to rewrite the checker and
all files can still undermine them. These ordinary files are not an OS sandbox.
For a live delegated trial, place the oracle and review process under independent
control, as the book's authority boundary requires.

The only intended learner edits here are the two working-copy spec files.
Keep `shared/`, `fixtures/`, `evidence/`, the checker and every existing
`repo/` or `reader_side/` file unchanged. The exercise adds no payment behavior,
threshold change, release or fictional approval to the cumulative application.

## What the checker can miss

The checker enforces a deliberately controlled representation. It compares the
fixed requirement wording after whitespace normalization; selected source/owner
fields; scope/status/value metadata; case inputs and outputs; and requirement
references in plan/tasks. It rejects symlinked artifact substitutions. It does
not prove arbitrary natural-language equivalence, implementation correctness,
adequacy of user language or complete architectural traceability. A valid
paraphrase may need human review rather than acceptance by this small checker.

The fourteen negative controls do not count as fourteen model trials. They test
the checker itself. Run them with:

```bash
python3 -m unittest discover -s practice/sdd -p test_check.py -v
```

## Review the ambiguity, then explain the repair

Before looking at the worked answer, answer these questions in plain language:

1. The sponsor said "below EUR 5000." Which source settles equality, and why is
   the sponsor's wording not enough?
2. Which artifact in each flow should contain the observable answer? Which plan
   or task needs to refer to it?
3. Why can a structurally valid specification remain incomplete? What would a
   second tool looking only at the same incomplete text miss?
4. Does fixing the equality example settle operator vocabulary, measured benefit,
   implementation approval or release? State the remaining decision owner.

**Worked feedback:** SRC-POL-001 and the fixed SC-EXPL-002 case require
HUMAN_REVIEW at exactly EUR 5000, with AT_OR_ABOVE_LIMIT and BR-001/v1. The
explanation still has no payment authority. Adding that case repairs a concrete
fidelity gap without changing the intended policy. It does not answer the three
open human-research questions or supply approval. A strong answer traces this
reasoning through both behavioral specs and task T02; merely reporting PASS
does not show that understanding.

## Evidence and remaining acceptance

See `evidence/RUN_INDEX.json`, exact stdout/stderr, package metadata/hashes,
dependency versions, scaffold snapshots and input/output inventories. Installation
failures are retained alongside successful retries. The snapshot preserves
generated local CLI assets with their upstream MIT notices; it contains no
installed dependency tree or credentials. `CLI_REPRODUCTION.md` records the
specific setup boundary and commands.

The [current d8 native packet](observed_native_20261022_d8/README.md) records the
full installed Spec Kit command in OpenCode, complete fixed-input attachment,
genuine first failures and two disclosed same-session execution requests. The
last native response supplies all five requirements, eight exact cases and
three actual unanswered owner questions, then normally stops before planning.
The [independent review](native_review_20261022_d8/INDEPENDENT_R08_REVIEW.json)
supports closure of the original bounded R08 tutorial scope.

The useful body was returned as native assistant text and was not saved to the
project's spec file. That file contains only the rejected header/Input first
write. The checklist and feature metadata were not created; the response's
claim of three artifacts is false. The raw response and actual file are retained
separately. An editorial reader copy removes operational instructions, relocates
exact native authority sentences and deletes the false completion assertion,
with every change disclosed in its diff. It adds no requirement or owner answer.
No interactive owner dialogue, separate speckit.clarify invocation, human
acceptance or implementation readiness is claimed.

The [earlier d7 packet](observed_native_20261022/README.md) remains unchanged as
the dated provider-failure, non-action response and full-input-read/timeout
observation. It was partial at that stopping point. The separately dispatched
ChatGPT generation below retains its own provenance and is not relabeled as
native client execution.

OpenSpec remains a clearly scoped unobserved native contrast. A second observed
route is required only before claiming a measured paired comparison. The
transfer prompts under transfer/ are immediate practice, not participants or
outcomes in Chapter 13's separate delayed-transfer study. The authored repair
exercise's NOT_RUN labels describe that fixture's own provenance, not the later
native observation.

## Generate from the scaffold with an actually dispatched agent

`create_agent_bundle.py` makes a fresh input packet from the **Spec Kit 1.2.2**
scaffold actually created on 21 October 2026. The new init and three Python helper
commands are retained in `evidence/revision_d4_framework_commands/`; each exited
0, with full before/after file inventories. The builder copies the blank templates, framework instructions, source
and fixed input obligations. It excludes the authored before/after answer
specimens. A full input inventory, the exact task prompt and the controller plan
are retained before any worker runs:

```bash
python3 practice/sdd/create_agent_bundle.py --output ../sdd-agent-01
python3 practice/orchestration/orchestrator.py \
  --plan ../sdd-agent-01/plan.json --inputs ../sdd-agent-01/inputs \
  --output ../sdd-agent-01/run \
  --worker-script practice/orchestration/external_worker.py
```

The second command waits for an external coordinator to dispatch real workers.
It does not call a model itself. Follow the submission recipe in
`practice/orchestration/README.md`. First a worker generates spec, plan and tasks;
then a separate worker reviews them against the fixed input sources. The
controller finally stops at `WAITING_HUMAN` (exit 3), because a model review
cannot complete requirements approval. Generation has one attempt and a
480-second limit; review has one attempt and 300 seconds. The whole run is
bounded at 900 seconds, and automatic retries are disabled.

When using ChatGPT collaboration, name that interface. Reading the pinned
framework templates through a dispatched agent is actual model generation
using those materials; it does not demonstrate native `/speckit-*` discovery or
execution in Codex, Copilot or Claude Code. The instruction to avoid neighboring
reference answers is a context restriction in a shared filesystem, not an OS
access barrier. Retain actual prior exposure, first outputs, reviewer findings
and any later correction as distinct attempts. No spontaneous model defect is
promised or injected.

The original `check.py` deliberately checks the authored repair exercise and its
`author_exercise` provenance. Do not change a live generation's provenance to
satisfy that checker. Assess the fresh output against the source requirements
and cases, retain the independent review, and keep human approval pending.
Use `validation/records/SDD_GENERATION_PAIR.json` to track the observed route and
the contrasting route's actual status. Its historical `PAIR` filename does not
require two observed runs for R08. This collaboration episode does not establish
native framework/client execution or a framework ranking.
