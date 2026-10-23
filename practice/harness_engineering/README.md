# Improve the harness around a fixed responder

This is an **original deterministic teaching adaptation** of the
Propose/Probe/Compose idea discussed in Harness². It runs actual Python
subprocesses and changes their behavior through harness configuration. It uses
**zero model calls**. The editor, responder, tasks and deliberate faults were
authored for the exercise. Its results are not an LLM benchmark, an independent
generalization experiment, or a reproduction of the Harness² paper.

The exercise answers a narrow engineering question: what evidence do we retain
when we change the system around a fixed task executor?

## Run it

Extract this edition into a new directory and run from its **untouched
`companion/` directory**. Keep your cumulative study copy and its completed work
separate. Do not use `reader_start.py new 1` for this experiment: that command
deliberately installs the faulty Chapter 1 router.

The five source pins include `repo/src/treasury/routing.py` and the learner
`repo/engineering/planning/delegation_plan.json`. Repairing either file in an
earlier exercise can legitimately make this experiment refuse the cumulative
copy. Run the following only from the fresh edition copy:

```bash
python3 practice/harness_engineering/run_experiment.py \
  --output ../my_harness_experiment_01
python3 -m unittest discover -s practice/harness_engineering/tests -v
```

Use a new output directory each time. Existing directories, symlinked output
path components, and destinations inside the core `repo/`, `reader_side/`,
or this exercise's `fixtures/` and `tests/` trees are refused before creation.
The experiment does not require an API key,
network connection or third-party Python package. It uses the existing Treasury
router as a fixed domain tool. Its five pinned source files must match this
edition; if a reader has changed the routing or planning exercise, preserve that
work and return to the fresh edition copy. Do not edit `SOURCE_PINS.json`, reset
a repaired candidate or rebaseline the experiment to bypass the refusal.
See `../../navigation/CHAPTER_ROUTES.md` for the return to the cumulative lab.

Start with `REPORT.json`, then inspect `COMPOSITION_DECISION.json`, the candidate
diffs and the individual process receipts. `observed/treasury_deterministic_v3/`
contains the final retained author run after the output-path and receipt fixes.
The earlier `observed/treasury_deterministic/` and
`observed/treasury_deterministic_v2/` remain as historical evidence.
Reproduction produces new timestamps and
elapsed times; the task outcomes and semantic counts should agree.

## The fixed task and the two editable levers

For each amount, return exactly four fields:

```json
{
  "route": "STANDARD_QUEUE",
  "reason": "BELOW_LIMIT",
  "policy_version": "BR-001/v1",
  "payment_authorized": false
}
```

The actual `repo/src/treasury/routing.py` is copied and hashed before execution.
The router uses `Decimal`, rejects nonfinite or nonpositive amounts, and applies
the existing strict EUR 5,000 boundary. The task does not repair this router,
change business policy or authorize a payment. The protected policy record,
acceptance file and both CP07 plan files retain their original bytes.

The fixed responder has an intentionally poor fallback: estimate the route
using binary floating-point arithmetic and omit fields unless configured to
emit them. Candidate harnesses can change only the routing strategy, the
selected response fields and a bounded memory of development observations.
They cannot supply commands, file paths, a new policy threshold or a runtime
budget. A policy-edit proposal and a budget-edit proposal are retained as
rejections before any subprocess runs them.

This simplified executor makes the effects inspectable. It does not model
the full behavior of a language model or optimize all eight Harness² components.

## Walk one refinement step

1. **Observe the baseline.** Run four development inputs. For `NaN`, the
   shortcut emits `{"route": "HUMAN_REVIEW"}`: an incorrect route and an
   incomplete response. Its trace shows that the domain tool was never called.
2. **Propose and probe components.** The tool-first proposal calls the real
   router but still omits three fields. The schema-complete proposal emits the
   required fields but still uses the faulty shortcut. Each proposal is run in
   a fresh subprocess on the same development inputs.
3. **Keep a misleading candidate.** The memorization control stores observed
   development tool outputs. It produces complete correct development responses
   without learning how to handle a new amount. Its unseen-input fallback is
   still the original shortcut.
4. **Compose from visible behavior.** The deterministic composer selects the
   component that demonstrated a fresh router call for every development input
   and the component that demonstrated all required fields. It does not receive
   correctness scores or held-out inputs. These proxy checks motivate an edit;
   they do not establish semantic correctness.
5. **Adopt, then evaluate independently.** Freeze the composed configuration and
   the improvement-library entry. Only then compare outputs with the separate
   manually authored oracle, including eight inputs not passed to the composer.
6. **Reuse experience on later inputs.** Start with a fresh baseline and propose
   components from the retained entry. Reuse requires the same router identity
   and output contract. Three later cases run without new probing. A changed
   router identity is explicitly rejected as a stale lesson.

The central composition is deliberately short:

```python
tool_source = max(ids, key=tool_scores.get)
shape_source = max(ids, key=shape_scores.get)
result = copy.deepcopy(candidates[tool_source])
result["response_fields"] = copy.deepcopy(
    candidates[shape_source]["response_fields"]
)
result["development_memory"] = {}
```

Read the surrounding checks in `run_experiment.py`: a component is not adopted
unless every development trace supports its stated proxy criterion. The fixed
heuristic is part of the teaching design, not something learned during this run.

## What the retained run shows

The run uses four development inputs, eight held-out inputs and three later
inputs. The held-out values include zero, infinity, invalid text, negative values
and `4999.9999999999999999999`. Converting the latter to a float rounds it to
5000, while the actual decimal router correctly treats it as below the boundary.

| Harness | Correct development routes | Complete correct development responses | Correct held-out routes | Complete correct held-out responses |
|---|---:|---:|---:|---:|
| Fixed baseline | 2/4 | 0/4 | 4/8 | 0/8 |
| Tool-first only | 4/4 | 0/4 | 8/8 | 0/8 |
| Complete fields only | 2/4 | 2/4 | 4/8 | 4/8 |
| Memorized development | 4/4 | 4/4 | 4/8 | 4/8 |
| Composed | 4/4 | 4/4 | 8/8 | 8/8 |

The retained improvement components also produce complete correct responses for
the three later inputs. The complete run launches 63 Python workers, makes 27
calls to the fixed Treasury tool and makes zero model calls. Counts and individual
outcomes are recorded in `observed/treasury_deterministic_v3/REPORT.json` and its
process/evaluation receipts. Local elapsed time is recorded; tokens, model bills
and human effort are unknown rather than estimated.

These are deliberately constructed fixture results. The development and
held-out split concerns what the composer receives. The exercise authors knew
the cases, so the split supplies a reproducible overfitting illustration, not
a blind or statistical estimate of generalization.

## Follow the evidence

| Artifact | What it contains |
|---|---|
| `SOURCE_RECEIPT.json` | Exact source, runtime and fixture identities; scope of protection |
| `TASK_CONTRACT.json` | Public response contract, separate from expected answers |
| `RUNTIME_BUDGET.json` | Owner-controlled process and timeout ceilings |
| `candidates/NAME/harness.json` | Each accepted configuration |
| `candidates/NAME/change.diff` | Its difference from the fixed baseline |
| `probes/NAME/PHASE/CASE.json` | Actual argv, request, stdout, stderr, exit/timeout, elapsed time and tool trace |
| `rejected_proposals/` | Invalid policy and budget proposals with rejection reasons |
| `IMPROVER_INPUT.json` | Complete input seen by the deterministic composer; no held-out cases or correctness scores |
| `COMPOSITION_DECISION.json` | Proxy criteria, observed counts and chosen components |
| `ADOPTION_RECEIPT.json` | Configuration identity fixed before held-out execution |
| `evaluation/` | Independent route and exact-response assessment, created after adoption |
| `improvement_library/entry_001.json` | Reusable components, lesson, source dependency and supporting evidence |
| `improvement_library/rejected_stale_reuse.json` | Refusal to reuse the entry after its source changes |
| `REPORT.json` | Counts, results and limitations |
| `OUTPUT_SHA256.json` | Identities of all completed output artifacts |

The runtime passes only the selected task, configuration and fixed router path
to the worker. The editor function receives the serialized `IMPROVER_INPUT`.
The separate oracle is not passed to either function. This is separation within
reviewable trusted code; it is not OS-enforced confidentiality from an arbitrary
program running under the same account. Read-only mode bits and hashes detect
selected changes but do not create a security sandbox. Hashes establish identity,
not the truth of a policy or trustworthiness of an external timestamp.

Task IDs are validated as unique filesystem-safe identifiers before any probe
path is created. Raw stdout, stderr and exit/timeout evidence are saved before
parsing the worker response; malformed JSON or mismatched identities therefore
leave a rejected receipt instead of erasing the attempted execution.

## Relationship to Harness²

The primary research describes task-level harness refinement through
Propose/Probe/Compose and a persistent improvement harness that informs future
refinement. Its model weights stay fixed. This exercise borrows that structure:
the candidate configuration is the execution harness; the retained components,
lessons and dependencies inform a later proposal from a fresh baseline.

The differences matter. Our proposer and composer are deterministic functions;
the executor is a small deterministic responder; the task family and candidate
faults are authored; only two main behavior levers are improved. Our schema check
uses the public task contract. Development tool outputs construct the
memorization negative control, while independent acceptance scores do not guide
composition. This is a behavior-guided teaching adaptation, not an experimental
replication of the paper's model-driven, no-ground-truth-feedback method.

For the upstream project and its separately recorded demonstration, follow the
book's accompanying upstream-demo record. Do not transfer these fixture gains
to a coding model, another task family or production deployment.

Primary sources checked for the book on 20 October 2026:

- Ruiyao Xu and colleagues, *Harness²: Recursive Agent Harnessing for an Open
  World*, arXiv:2610.14224, https://arxiv.org/abs/2610.14224.
- Official implementation and experiment guide:
  https://github.com/google-research/harness2 and
  https://github.com/google-research/harness2/blob/main/docs/EXPERIMENTS.md.

This directory contains original teaching code. No upstream source code is
copied into it.

## Exercises

1. Inspect the complete-field candidate. Explain why a structurally correct
   response can still violate the routing contract.
2. Compare the memorization control with the composed candidate on the precise
   decimal boundary. Which trace evidence distinguishes them before an oracle
   score is available? Which correctness questions remain unanswered?
3. Propose an additional harness component and an input on which it might make
   things worse. Keep the new evaluation independent and record any exposure of
   its expected answers to the improver.
4. Replace the deterministic editor or responder only in a separate extension.
   Pin its version and budget, retain all attempts, and report actual model calls
   and bills. A model-backed result requires its own evidence and cannot inherit
   the deterministic run's claimed outcome.

T07-03 remains pending in the protected CP07 plan; T07-04 remains blocked.
This extension does not alter those records or grant release authority.
