# MEAS-014/v1 contract

The measured unit is one declared local command attempt in the CP13 handoff
workflow. The logical work item is HANDOFF-013. Three green reviews of it are
three attempts, not three accepted outcomes. A protected synthetic owner rule
accepts only its exact final artifact and A05 evidence; actual human acceptance
is unknown.

From the companion root:

```bash
python3 reader_side/tools/rehearse_measurement.py \
  --incident-rehearsal CP12_SESSION --transfer-session CP13_TRANSFER \
  --output NEW_MEASUREMENT
python3 reader_side/tools/measurement_gate.py \
  --measurement-session NEW_MEASUREMENT --output NEW_REVIEW \
  --scope-baseline CP14_BASELINE
```

Use `--reference` on both commands for selected protected examples and matching
CP12/CP13 reference sessions. The gate also accepts `--unsafe-control` and
`--receipt prior/MEASUREMENT_RESULT.json`. Current and reference sessions cannot
certify one another. Output directories must be new and outside source/prior
evidence. The rehearsal writes `MEASUREMENT_SESSION.json`; the gate writes
`MEASUREMENT_RESULT.json` with `PASS_MEASUREMENT_REVIEW_ONLY` on success.

## Observation boundary and raw evidence

A01 runs a faulty review and records rejection. A02 restores the actual current
CP13 candidates in its disposable copy, or selects the protected reference, and
records green review. A03 repeats that review for the same item. A04 creates
fresh transfer evidence from the same CP12 session, then tests the old A02
receipt against the new evidence and records staleness. A05 reviews the fresh
evidence. Both commands within A04 belong to its observation/accounting boundary.

Numbered immutable records preserve command arguments, exit/status, source and
artifact identities, stdout/stderr hashes, monotonic start/end/duration, and a
previous-record hash. Repair/selection and final synthetic-owner actions are
also recorded. Earlier evidence is never rewritten. The hash chain and receipt
operate under local owner control; they are not an external timestamp or
authenticated field-study attestation. Nested subprocess time is included in
its top-level command duration and is not counted a second time.

These observations are local process timing and review mechanics, not DORA
production-delivery metrics. Human developer, reviewer and rework hours, actual
vendor/compute bills and real accepted outcomes remain null/UNKNOWN. The tool
does not convert process seconds to human hours or infer zero charges.

## Synthetic cost and sensitivity fixture

All scenario quantities are nonnegative finite decimal strings. Currency must
be consistently EUR; there is no implicit currency conversion. Initial effort,
review and implementation rework are disjoint accounting categories. The
fixture records every A01–A05 attempt, including failed and repeated attempts.

| Attempt | Initial hours | Review hours | Rework hours | Vendor EUR | Compute EUR |
| --- | ---: | ---: | ---: | ---: | ---: |
| A01 | 0.20 | 0.10 | 0 | 0.02 | 0.01 |
| A02 | 0 | 0.10 | 0.15 | 0.03 | 0.01 |
| A03 | 0 | 0.05 | 0 | 0.01 | 0.01 |
| A04 | 0 | 0.05 | 0.05 | 0.01 | 0.01 |
| A05 | 0 | 0.05 | 0.10 | 0.02 | 0.01 |

Initial/rework rates are EUR40/hour and review EUR50/hour: EUR8 initial,
EUR17.50 review, EUR12 rework, EUR0.09 vendor and EUR0.05 compute, totaling
EUR37.64. One applicable final synthetic acceptance gives EUR37.64 per accepted
outcome. A conditional EUR50 ceiling produces GO for this base scenario.
An additional 0.50 rework hour gives EUR57.64 and CHANGE. With no retained
accepted outcome, cost per accepted outcome is UNDEFINED and the scenario
returns STOP; it never divides by zero or reports zero cost.

The actual decision is CHANGE: propose a small owner-approved pilot to collect
missing effort, accepted-output and billing records and compare matched work
with the local control. Conditional scenario GO/STOP do not authorize a real
pilot, procurement, release, reconciliation or expansion.

## Cumulative check

```bash
python3 reader_side/tools/run_checks.py \
  --incident-rehearsal CP12_SESSION --transfer-session CP13_TRANSFER \
  --measurement-session NEW_MEASUREMENT --require-measurement \
  --output NEW_COMBINED_RESULT.json
```

This requires actual current CP01–CP09, CP11, CP12, CP13 and CP14 readiness and
the same nominated CP12/CP13 identities. CP10 release remains separate; changes
to either CP14 candidate invalidate an earlier applicable CP10 source receipt.
