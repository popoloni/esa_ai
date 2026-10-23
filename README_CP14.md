# Chapter 14: Measure outcomes and choose a tool stack

This final exercise measures a declared local CP13 workflow and reviews a
proposed tool pilot. Actual command durations, protected synthetic acceptance,
scenario costs and unavailable field measurements have distinct fields and
meanings. Nothing here establishes human productivity, actual vendor cost,
measured ROI or an empirical market winner.

Use Python's standard library and the same local Git required by the cumulative
lab. No vendor client, model API, telemetry exporter, invoice integration or
network call is used. Run commands from this `companion/` directory.

## What is measured

The logical work item is HANDOFF-013. Five attempts run on a disposable copy of
the current CP13 workflow:

| Attempt | Observed action | Expected gate result |
| --- | --- | --- |
| A01 | Submit a faulty CP13 review | FAIL |
| A02 | Restore the caller's exact current CP13 artifacts and review | PASS |
| A03 | Review the same item again | PASS |
| A04 | Create fresh transfer evidence, then check the earlier A02 receipt against it | FAIL: stale receipt |
| A05 | Review the fresh transfer and current artifacts | PASS |

A04 includes two actual top-level subprocesses; the other attempts include one.
The local telemetry therefore records six commands, five gate attempts and
three green reviews. Nested child-process time is included in its top-level
duration and is not added a second time. The initial faulty selection and
repair/selection action are also retained. The accounting boundary covers these
five attempts, not all prerequisite construction, book authoring or validation.

Numbered raw JSON records retain arguments, exits, result/source/log digests,
actual monotonic nanoseconds and a previous-record hash. Every earlier output
remains preserved. The fresh transfer and nominated original transfer both bind
the same CP12 incident session. Replacing evidence does not silently renew an
old green receipt.

## Two editable records

WO-014 permits only:

- `repo/engineering/measurement/outcome_review.json`
- `repo/engineering/measurement/tool_decision.json`

The supplied records intentionally count repeated passes as accepted items,
turn missing actual costs into zero and overclaim a tool/release decision.
Protected worked examples and stable unsafe controls remain outside candidate
control. Preserve all prior router, PolicyStore, incident and learning code.

The measurement session excludes these two interpretation candidates from its
source inputs so you can fill them after observation. Gate receipts include
their exact bytes. CP10's cumulative source binding also includes them, so
repairing them makes an applicable earlier CP10 receipt stale.

## Run the current-source exercise

Complete the earlier current CP01–CP09, CP11, CP12 and CP13 candidates and retain
matching current CP12/CP13 sessions. Use new output paths for every attempt:

```bash
python3 reader_side/tools/scope_guard.py --chapter CP14 \
  --capture reader_side/evidence/CP14_EDIT_BASELINE.json
python3 reader_side/tools/rehearse_measurement.py \
  --incident-rehearsal reader_side/evidence/CP12_CURRENT \
  --transfer-session reader_side/evidence/CP13_TRANSFER \
  --output reader_side/evidence/CP14_MEASUREMENT

# Inspect all attempts, then edit only the two CP14 interpretation records.
python3 reader_side/tools/measurement_gate.py \
  --measurement-session reader_side/evidence/CP14_MEASUREMENT \
  --scope-baseline reader_side/evidence/CP14_EDIT_BASELINE.json \
  --output reader_side/evidence/CP14_REVIEW
python3 reader_side/tools/measurement_gate.py \
  --measurement-session reader_side/evidence/CP14_MEASUREMENT \
  --receipt reader_side/evidence/CP14_REVIEW/MEASUREMENT_RESULT.json \
  --output reader_side/evidence/CP14_RECEIPT_RECHECK
```

The rehearsal status is `MEASUREMENT_RECORDED_REVIEW_ONLY`; a successful gate is
`PASS_MEASUREMENT_REVIEW_ONLY`. Capture the edit baseline before changes. A gate
without it cannot establish the actual before/after scope. Keep baselines and
raw evidence under reader control; the local file checks are not an OS sandbox
or an independently authenticated field-study attestation.

`MEASUREMENT_SESSION.json` binds `incident_session_sha256`, the nominated
`seed_transfer_session_sha256`, and the distinct `final_transfer_session_sha256`.
Inspect `raw/000001.json` onward, `logs/`, `attempts/A01` through `attempts/A05`,
`refreshed_transfer/`, `artifacts/FINAL_ARTIFACT.json` and
`SYNTHETIC_OWNER_ACCEPTANCE.json`. The gate retains `LOCAL_TELEMETRY.json` and
`SCENARIO_COSTS.json` beside `MEASUREMENT_RESULT.json`.

For a protected worked example, nominate matching CP12/CP13 reference sessions
and add `--reference` to both commands. The reference rehearsal selects stable
faulty/reference controls and never edits protected source. `--unsafe-control`
on the gate must fail against that reference measurement after current repairs.
Reference sessions cannot certify the working candidates.

## Costs, accepted outcomes and unknowns

Three green machine reviews are not three accepted outcomes. The protected
synthetic owner rule accepts one exact final logical item, artifact and A05
receipt. The earlier A02/A03 evidence does not remain current after A04's fresh
transfer. Actual human acceptance remains unknown.

Human initial, review and rework hours, actual vendor/compute bills and actual
cost per accepted outcome are null/UNKNOWN. Measured process nanoseconds never
populate those fields or imply free labor/services. These local observations
are not DORA production-delivery metrics.

The separate scenario ledger includes all five attempts. Declared initial and
rework effort cost EUR40/hour; review costs EUR50/hour. Total initial effort is
0.20h, review 0.35h and rework 0.30h, in nonoverlapping categories. Vendor and
compute assumptions add EUR0.09 and EUR0.05. The exact Decimal result is
EUR37.64, with per-attempt costs 13.03, 11.04, 2.52, 4.52 and 6.53.

At one synthetic accepted item, the base scenario is EUR37.64/item and a
conditional GO under a declared EUR50 ceiling. An extra 0.50 rework hour gives
EUR57.64 and CHANGE. With no retained acceptance, cost remains EUR37.64 but cost
per accepted outcome is UNDEFINED and the scenario says STOP. The code rejects
nonfinite/negative values, floats, mixed currencies, missing quantities,
duplicated/omitted attempts and invalid denominators. It makes no implicit
currency conversion. Monetary display uses ROUND_HALF_UP; decision comparisons
use unrounded Decimal totals.

The actual proposed pilot decision remains CHANGE: collect missing field
evidence before expansion or a tool-stack selection. Conditional scenarios do
not authorize a real pilot, procurement or release.

## Tool capabilities and future field collection

`reader_side/measurement/tool_capabilities.json` records dated primary-doc
capabilities and constraints for VS Code Copilot, GitHub Copilot cloud agent and
Claude Code, alongside the separate local control. Vendor rows explicitly say
DOCUMENTED_NOT_EXECUTED, with comparative performance, costs and human effort
unknown. Recheck the sources and local permissions before a real pilot.

For future Pilot E collection, copy `FIELD_TELEMETRY_TEMPLATE.json` outside
protected source and use `FIELD_TELEMETRY_SCHEMA.json` and
`FIELD_TELEMETRY_PROTOCOL.md`, all under `reader_side/measurement/`. Retain raw
self-reported effort intervals, resource deviations, billing evidence and
applicable owner acceptance/withdrawal records. Reconcile overlapping effort,
allocations and currencies before analysis. The delivered template is empty;
it neither feeds the synthetic calculation nor establishes a field result.

## Require the current cumulative workflow

```bash
python3 reader_side/tools/run_checks.py \
  --incident-rehearsal reader_side/evidence/CP12_CURRENT \
  --transfer-session reader_side/evidence/CP13_TRANSFER \
  --measurement-session reader_side/evidence/CP14_MEASUREMENT \
  --require-measurement --output reader_side/evidence/CP14_COMBINED.json
```

This requires actual current CP01–CP09, CP11, CP12, CP13 and CP14 readiness, the
same nominated CP12 identity and the exact original CP13 seed identity. CP10
release remains separate and NOT_RUN unless nominated. CP07 stays pending/
blocked; incident reconciliation, the human learning pilot, rubric validity
and real pilot approval remain pending.

From the book-package root, run `python3 scripts/validate_chapter14_lab.py` for a
new `build/chapter14_validation` output, or provide `--output NEW_PATH`. It uses
disposable copies, preserves delivered starters and prior evidence, exercises
current/reference/unsafe modes and stale/tampered inputs, then runs the shared
suite once. The JSON summary records actual counts and source preservation;
scenario assertions are not added to the unit-test count.
