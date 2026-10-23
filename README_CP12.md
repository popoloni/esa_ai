# Chapter 12 — Investigate incidents and recover operations

INC-012 is a new synthetic deployment rehearsal over the same CP11 SQLite
`PolicyStore`. The original router, history implementation and policy catalogue
are retained. The faulty deployment selects a different, absent state file and
allows initialization. That file starts at BR-001/v1 while the intended ledger
already contains v1 history and has v2 active.

The editable CP12 paths are:

- `repo/engineering/operations/deployment.json`
- `repo/engineering/operations/incident_review.json`

The protected work order is `reader_side/operations/WORK_ORDER_CP12.md`.
`reader_side/reference_solution/ch12/` contains the worked configuration and
causal review. Stable unsafe fixtures live in `reader_side/operations/`; they
remain faulty after a learner repairs the working candidates.

## Observe the protected worked example

Run from this **companion directory**, with Python 3 and no `PYTHONPATH` setup:

```bash
python3 reader_side/tools/rehearse_incident.py \
  --reference --output reader_side/evidence/CP12_REFERENCE_SESSION
python3 reader_side/tools/incident_gate.py \
  --reference --rehearsal reader_side/evidence/CP12_REFERENCE_SESSION \
  --output reader_side/evidence/CP12_REFERENCE_REVIEW
```

Every output directory must be new. For a later run choose a new name; do not
delete earlier evidence to reuse it. This mode selects the protected CP11
worked example. It does not establish readiness of the current CP11 or CP12
learner candidates. Expected gate status is
`PASS_INCIDENT_RECOVERY_REVIEW_ONLY`; the rehearsal itself reports
`FAULT_REPRODUCED_REVIEW_ONLY` when the fault is independently observed.

The session stores `INCIDENT_SESSION.json`, actual SQLite files under
`state/control/`, `state/incident/`, preserved copies under `state/preserved/`,
configuration snapshots under `inputs/`, and individual `steps/*.json` and
`steps/*.log` files. The gate writes `INCIDENT_RESULT.json`, fresh copied state,
recovery steps, and separately retained guard/new-request probe copies. Gate
evaluation leaves the original rehearsal directory byte-identical.

## Read the causal evidence

The telemetry schema is `cp12-service-event/v1`. It is standard-library JSON
from separate real Python worker processes, not OpenTelemetry SDK/OTLP/exporter
output. Fields record process ID, UTC timestamp, Python/platform, operation and
arguments, actual resolved database path, selected relative path,
configuration/source hashes, database existence, state hashes/counts/rows,
active policy, outcome and error. The logs contain only synthetic data.

| Evidence | Question answered |
| --- | --- |
| `S01_seed_history`, `S01b_seed_anchor`, `S02_activate_v2`, `S03_seed_current` | What history and active policy existed before the fault? |
| `S04_control_current` versus `S06_fault_current` | With the same source/request and other settings, does changing only the state path explain the route? |
| `S05_control_history` versus `S07_fault_history` | Is an equal deterministic decision ID a real replay, or a new decision in another ledger? |
| `S08_incident_retry` | Does a second retry within that wrong ledger preserve the record and audit count? |
| `S09_explicit_v2` | Can the same code apply v2 correctly even while that ledger's active default remains v1? |
| `S10_recompute` | Does recorded v1 history still recompute under its original policy? |

The path-only control keeps the faulty initialization setting and absent
binding guards unchanged. It isolates a cause. The later recovery configuration
adds guards as a distinct change. The `rollout_anchor` key is a retained v1
EUR5,000 record absent from the incident ledger; its presence is a teaching
precondition, not an authenticated globally unique ledger identifier. The owner
gate also binds exact database bytes and preserved records.

## Repair the current cumulative lab

First complete the earlier exercises, including CP11 under its own scope.
The CP12 exercise does not authorize edits to `policy_history.py` or
`routing.py`. Create a current-mode session and capture the baseline before
editing the two CP12 paths:

```bash
python3 reader_side/tools/rehearse_incident.py \
  --output reader_side/evidence/CP12_CURRENT_SESSION
python3 reader_side/tools/scope_guard.py --chapter CP12 \
  --capture reader_side/evidence/CP12_BEFORE_EDIT.json
python3 reader_side/tools/incident_gate.py \
  --rehearsal reader_side/evidence/CP12_CURRENT_SESSION \
  --scope-baseline reader_side/evidence/CP12_BEFORE_EDIT.json \
  --output reader_side/evidence/CP12_STARTER_REVIEW
```

The starter review must fail. Its deployment still selects the incident ledger;
its review blames a code regression, proposes deleting incident evidence, and
claims closure. Repair the deployment to select `state/control/history.sqlite`,
set `initialize_missing_state` to `false`, require active `BR-001/v2`, and require
`rollout_anchor`. Complete the hypothesis log with evidence-backed conclusions
for threshold regression, retry implementation, and wrong state selection. The
protected worked review shows the required stable evidence IDs and boundaries.

Then run into another new output directory:

```bash
python3 reader_side/tools/incident_gate.py \
  --rehearsal reader_side/evidence/CP12_CURRENT_SESSION \
  --scope-baseline reader_side/evidence/CP12_BEFORE_EDIT.json \
  --output reader_side/evidence/CP12_REPAIRED_REVIEW
python3 reader_side/tools/run_checks.py \
  --incident-rehearsal reader_side/evidence/CP12_CURRENT_SESSION \
  --require-operations \
  --output reader_side/evidence/CP12_COMBINED_RESULTS.json
```

The combined requirement includes actual current CP01–CP09 and CP11 readiness
as well as the CP12 gate for a `WORKING_CANDIDATES` session. A protected-reference
session cannot certify current candidates. CP10 release status stays separate;
without a nominated release rehearsal it is `NOT_RUN`. A passing regression
suite alone is not a passing incident review.

## Recovery and freshness

`R01`–`R06` inspect the selected state, retry old/current requests, recompute v1,
reject a changed-payload retry, and reopen in another process. These operations
must preserve both retained ledgers. `R07` creates a fresh v2 request on a
separate probe copy. `G01`–`G03` prove missing state, wrong active policy, and a
missing historical anchor are rejected before accidental initialization or
history mutation. Escaping and symlinked paths are refused.

```bash
python3 reader_side/tools/incident_gate.py \
  --rehearsal reader_side/evidence/CP12_CURRENT_SESSION \
  --receipt reader_side/evidence/CP12_REPAIRED_REVIEW/INCIDENT_RESULT.json \
  --output reader_side/evidence/CP12_RECEIPT_RECHECK
```

The receipt binds the selected CP11 source, router, catalogue, owner inputs,
CP12 configuration/review, session identity, databases, logs and other evidence.
Changed inputs, malformed receipts, substituted state or altered logs fail
closed. A comment-only source change still requires fresh evidence. Output may
not nest inside the rehearsal or an earlier receipt's directory. Hashes support
owner-controlled consistency checks; they do not authenticate evidence against
an actor who controls the harness, manifest and host.

Successful local findings are reported separately:

- Restoration: `VALIDATED_LOCAL_SELECTION`.
- Reconciliation: `QUARANTINED_PENDING_OWNER_RECONCILIATION`.
- Guard validation: `LOCAL_GUARD_VALIDATED_NO_PRODUCTION_ROLLOUT`.

Incident-only rows are retained without automatic merging, deduplication or
deletion. Restoration does not declare their business effects reconciled. CP07
T07-03 remains pending and T07-04 blocked. No real production recovery, release,
payment, human acceptance, policy-v2 rollout, or incident closure is authorized.
Changes to the CP12 deployment/review also invalidate applicable CP10 source
receipts; the CP10 presentation experiment never authorizes operations.

## Reproducible validation

From the book root, run the script on disposable copies:

```bash
python3 scripts/validate_chapter12_lab.py \
  --output build/chapter12_validation_01
```

The output directory must be new. The validator records starter/repaired gates,
causal and guard observations, stale/malformed/substituted evidence failures,
actual CP12 edit scope, source preservation, and one current cumulative runner
result. Delivered starters, earlier checkpoint snapshots and original ledgers
are not repaired in place.
