# What did this change cost from preparation to a decision?

A successful patch is only one event in a workflow. You may spend time preparing the task, investigating an unsuccessful attempt, checking the result, explaining it to a reviewer and repairing it again. This practice records those events as they happen. Its purpose is to make a small cost account inspectable, including what remains unknown.

Start with one bounded change and one question: **what work and money can I attribute to this outcome?** Define the beginning, the decision at the end, and any work outside that boundary. Record preparation before starting the implementation. Preserve failed attempts. A later check of the same logical change is another review event, not another delivered item.

The recorder uses Python's standard library. It has no provider integration and makes no model calls. The original observed CSV account remains in `../csv_export/observed/agent_01/WORKFLOW_COST_ACCOUNT.json`; its unmeasured historical values have not been replaced by estimates. This module supports prospective collection and includes the completed technical maintenance observation below.

## Inspect a real maintenance account

`observed/guide_identity_01/` retains the repair of two stale protected-guide identities on 22 October 2026. Its `TASK.txt` defines the observation before preparation: supplied defect report through the exact repair, independent AGENT technical decision and recording. Earlier discovery/archive recovery and later release production remain separate. Read `ACCOUNT.json`, `REPORT.json`, `RECORDING.json`, `REVIEW.json` and `ACCOUNT_AUDIT.json` together; all referenced evidence travels with the account.

The bounded workflow elapsed **534.138788 seconds**. Five wall intervals cover preparation, implementation, focused checks, independent agent review and recording. They include waits and do not measure active labor or active model execution. The original failing doctor and diagnostic error are retained. Twelve focused checks and 18 independent checks passed, all 211 other protected files and 37 repository files stayed unchanged, and the deliberately faulty seven-case starter remained three passes, two failures and two errors. Guide/oracle tampering was still detected. No candidate rework was required.

The account records one accepted technical item under decision kind `AGENT`. Human review was not performed or required by this scoped technical task; human acceptance remains unobserved. Model tokens, model charges and infrastructure bills were unavailable. Monetary coverage remains unknown, and complete money, cost per human-accepted item and ROI remain `null`. This observation does not complete the earlier interrupted native-client account or replace human reader sessions.

From the companion root, reproduce the report without changing the closed account:

```bash
python3 -B practice/workflow_cost/workflow_cost.py report \
  practice/workflow_cost/observed/guide_identity_01/ACCOUNT.json
```

The recorder checks referenced file hashes and accounting consistency. The independent audit checks the declared task boundary and evidence. Neither authenticates human identities, supplies absent bills or establishes a general productivity result.

## Three quantities with different meanings

| Quantity | How this practice obtains it | What it means |
| --- | --- | --- |
| Workflow elapsed time | Account start to finish, using recorded UTC clocks | Calendar interval, including gaps and waiting |
| Recorded interval coverage | Union of completed intervals, even when actors overlap | The part of the timeline covered by retained observations |
| Human active effort | Explicit human intervals, unioned per person and summed across people | Declared active work under the collector's stated method |

An agent's interval does not reveal active model execution. A tool process duration does not reveal the time a person spent thinking. The JSON keeps these meanings separate. UTC clocks can be affected by clock correction; reversed intervals are rejected, but the recorder cannot authenticate the machine clock. Use one clock source and retain any clock incident.

Two checks running for 30 seconds at the same time cover 30 seconds of elapsed time. They can still consume two processes and two charges. When two people each work for the same 30 seconds, the declared person effort is 60 seconds. The report therefore exposes raw interval sums for inspection but uses unions for elapsed coverage and for each person's overlapping effort records.

## Start before the work

Run from the companion root. Choose a new run directory for each observation. Keep the task statement and subsequent evidence immutable after they are referenced. Hashes bind evidence to the account: a changed file causes a refusal, rather than silently updating the record. Snapshot a mutable candidate before recording a decision about it.

```bash
mkdir -p work/cost_example
cp practice/workflow_cost/examples/TASK.txt work/cost_example/TASK.txt
python3 practice/workflow_cost/workflow_cost.py init \
  work/cost_example/ACCOUNT.json \
  --run-id COST-REHEARSAL-001 \
  --purpose "Check that the recorder preserves an automated result and its limits" \
  --interface "Local Python command line" \
  --boundary "Task reading through recorded local test result" \
  --exclusion "No human reading session, model request or attributable billing in this rehearsal"
python3 practice/workflow_cost/workflow_cost.py start \
  work/cost_example/ACCOUNT.json --id preparation-1 \
  --phase preparation --actor recorder-driver --actor-kind AUTOMATION \
  --evidence work/cost_example/TASK.txt
```

The supplied task is a recorder rehearsal, not a software change or human reading trial. If you are a human conducting your own run, use `--actor-kind HUMAN`, your anonymized collector ID, and an appropriate task statement. Use `AGENT` for an actual agent interval. The example's `AUTOMATION` value describes the retained subprocess-driven rehearsal. The CLI records identity declarations; it does not verify a person's identity or presence.

Read the task and select the command you intend to run. Close that preparation interval with evidence of what was prepared. Start the next interval before executing the check:

```bash
python3 practice/workflow_cost/workflow_cost.py stop \
  work/cost_example/ACCOUNT.json --id preparation-1 --outcome PASSED \
  --evidence work/cost_example/TASK.txt
python3 practice/workflow_cost/workflow_cost.py start \
  work/cost_example/ACCOUNT.json --id checks-1 \
  --phase verification --actor local-checker --actor-kind AUTOMATION \
  --evidence work/cost_example/TASK.txt
python3 -B -m unittest discover -s practice/workflow_cost \
  -p 'test_*.py' -v > work/cost_example/CHECKS.txt 2>&1
```

Inspect the actual command exit status and output before recording an outcome. `PASSED` is a collector declaration, not something inferred by the recorder. If a check fails, record `FAILED`, preserve its output and start a separate rework interval before making a correction.

```bash
python3 practice/workflow_cost/workflow_cost.py stop \
  work/cost_example/ACCOUNT.json --id checks-1 --outcome PASSED \
  --evidence work/cost_example/CHECKS.txt
cp practice/workflow_cost/workflow_cost.py work/cost_example/CANDIDATE.py
python3 practice/workflow_cost/workflow_cost.py accept \
  work/cost_example/ACCOUNT.json --id machine-decision-1 \
  --kind AUTOMATED --item recorder-candidate-1 --decision ACCEPTED \
  --reviewer local-unittest --candidate work/cost_example/CANDIDATE.py \
  --evidence work/cost_example/CHECKS.txt
python3 practice/workflow_cost/workflow_cost.py close \
  work/cost_example/ACCOUNT.json
python3 practice/workflow_cost/workflow_cost.py report \
  work/cost_example/ACCOUNT.json --output work/cost_example/REPORT.json
```

The expected result is a valid **partial account**. The automated denominator is one. Human acceptance, complete money and cost per human-accepted item are `null`; preparation and check intervals do not fill those gaps. No model work or participant session occurred. The retained execution of these commands is in `validation/CLI_EXERCISE.json`, with its final account and outputs under `validation/cli_rehearsal_02/`. The earlier validation against 25 controls is retained separately; the final run includes 28 controls and the report-output preservation guard.

## Extend the same account while it is open

Use `start` and `stop` for `implementation`, `verification`, `agent_review`, `human_review`, `rework` and `recording`, as well as preparation. Give each interval a unique ID. Intervals may overlap, but use one writer to mutate an account: this small CLI is not a concurrent event service. Retain all failed and abandoned intervals.

For a human collector who deliberately tracks active work, add `--measure DECLARED_ACTIVE_HUMAN_INTERVAL` to `start`. Stop an interval for a break or unrelated task. This records the collector's declaration, not automatically sensed attention. Agent and automation actors cannot use this measure or the `human_review` phase.

The `coverage` command states whether a phase is unknown, observed, not performed or not applicable. For example, after preserving a note that no rework occurred within a particular observation, record:

```bash
python3 practice/workflow_cost/workflow_cost.py coverage ACCOUNT.json \
  --category rework --state NOT_PERFORMED \
  --reason "No repair was attempted inside this declared boundary" \
  --evidence NO_REWORK_NOTE.txt
```

`NOT_PERFORMED` describes the observed boundary. It does not mean that historical effort was zero, or that an unobserved phase can be discarded. A completed interval automatically marks its phase observed but does not prove that you recorded every relevant activity. Review the boundary and exclusions yourself.

## Record usage, money and assumptions separately

Only import a quantity that an attributable source actually exposes. Provider token usage, a paid invoice, an allocation and a scenario rate are different inputs. The recorder never estimates tokens from characters or tool-output token counts.

```bash
python3 practice/workflow_cost/workflow_cost.py usage ACCOUNT.json \
  --id model-charge-1 --kind MONEY --component model --value 0.40 \
  --unit USD --charge-key invoice-123/line-4 --evidence INVOICE_EXTRACT.txt
python3 practice/workflow_cost/workflow_cost.py money-coverage ACCOUNT.json \
  --category model --state COMPLETE \
  --reason "This attributable receipt covers all model charges within the boundary" \
  --evidence RECONCILIATION.txt
python3 practice/workflow_cost/workflow_cost.py assume ACCOUNT.json \
  --name "Illustrative alternative hourly rate" --value 90 --unit USD/hour \
  --basis "Sensitivity scenario; not an observed payment"
```

These filenames and amounts illustrate syntax. They are not existing bills and must not be entered into an actual account without corresponding evidence. For usage quantities use `INPUT_TOKENS`, `OUTPUT_TOKENS` or `CACHED_TOKENS`, an integer value and `--unit tokens`. Keep them distinct; cached tokens can overlap a provider's input-token count. The recorder retains the reported categories and does not add them into a purported universal total.

Every money entry needs a distinct charge key. Reusing the same invoice line is rejected. Different currencies remain separate, with no assumed exchange rate. A complete total requires closed activity coverage and an explicit complete or not-applicable declaration for each of model, human and infrastructure money. An explicit zero is allowed only as an attributable amount, not as a replacement for unknown billing. Assumptions never enter observed totals.

## Count decisions about distinct items

`AUTOMATED`, `AGENT` and `HUMAN` are separate decision kinds. Each event names a logical item, the exact candidate bytes, a reviewer and the decision evidence. Repeated acceptance of the same item counts once. The latest event for that kind and item governs the report, so a later rejection removes its accepted count. An earlier event remains in the account.

For an actual human decision, the `accept` command additionally requires `--human-attestation` with the collector's attribution. This prevents accidentally reusing an automated command as human acceptance; it is not an identity or consent system. Retain the actual human decision and record that review effort. If the decision exists but review effort was not measured, keep that effort unknown and the whole-workflow total incomplete. A declaration that no human review occurred conflicts with human acceptance and is rejected.

An unobserved human denominator is `null`. An observed rejection gives a denominator of zero. Both prevent division; zero accepted outcomes does not give zero cost per accepted outcome. Only positive accepted counts and complete attributable money permit the descriptive ratio. Even then `roi` remains `null`: business benefit and a counterfactual require additional evidence outside this accounting exercise.

## Work through the specimen

`specimen/ACCOUNT.json` is a **synthetic teaching case**. Every time, person, task, charge and decision is invented, including Alex's review. Run:

```bash
python3 practice/workflow_cost/workflow_cost.py report \
  practice/workflow_cost/specimen/ACCOUNT.json
```

Its whole interval is 250 seconds. The individual intervals sum to 260 seconds because a check overlaps the repair by 10 seconds; their union is 250 seconds. The failed first check remains in the report. The two automated acceptances concern one logical item, so they contribute one outcome for that decision kind. The fictional human review covers 60 active seconds and accepts that same item once.

The invented receipts sum to USD 2.00. The separately stored USD 90/hour scenario assumption contributes nothing to that total. These numbers teach the arithmetic and boundaries; they are not observations of book readers, provider prices or the value of agentic development. `make_specimen.py` regenerates this clearly labeled specimen. It never rewrites an actual run.

## Verify and preserve

```bash
python3 -B -m unittest discover -s practice/workflow_cost -p 'test_*.py' -v
```

The controls cover reversed and timezone-free intervals, overlapping elapsed time and person effort, duplicate charges, unknown money, mixed currencies, failed work, repeated outcomes, source changes, absent human acceptance and invalid ROI claims. They test accounting boundaries, not whether a purported person or invoice is truthful.

Close only after collecting the intended observations and reconciliation. A closed account cannot be mutated through this CLI. Preserve its referenced evidence beside it; moving the complete directory together preserves its relative paths. For work or billing collected later, create a separately identified observation and explicitly relate its boundary to the earlier account. Do not rewrite old unknowns or timestamps to make the earlier account look complete.

## Inspect an actual AI-only rehearsal account

`observed/reader_rehearsal_01/account.json` records a prospectively started, bounded
AI reader-route rehearsal through root review and three instruction corrections.
Its preparation, failed attempts, task output, source snapshots, correction checks
and reconciliation are retained alongside the account. Run `report` on that file
to inspect the remaining unknowns. The four rehearsal scopes include only entry
and a handoff for Chapter 7; they do not complete its core exercise.

The retained AGENT decision concerns one correction snapshot, accepted by the root
agent who also made the edits. It is not independent human acceptance. The time
intervals include orchestration, waiting, concurrent work and delayed recording of
completion. They are not active model time, novice task time or person effort.
Human review was not performed, and attributable provider usage and money remain
unknown. Earlier book and kit preparation, and later full release work, are outside
this stated boundary. The account demonstrates inspectable recording; it does not
establish a whole-workflow financial result or a learning improvement.
