# WO-012: investigate a synthetic deployment and recover state selection

This owner-controlled work order authorizes a local teaching experiment using
the existing CP11 `PolicyStore`. It authorizes only these CP12 candidate paths:

- `repo/engineering/operations/deployment.json`
- `repo/engineering/operations/incident_review.json`

Capture a CP12 before-edit baseline. Do not change the original router, policy
history implementation, policy catalogue, earlier tests, owner fixtures, or
receipts while repairing this deployment. Finish CP11 under its own profile
before capturing the CP12 baseline. A protected reference mode is available for
a separate worked-example demonstration; it cannot certify working candidates.

## Incident and causal question

INC-012 is a newly seeded synthetic incident, not a report of a real deployment.
The original SQLite ledger contains v1 decisions and has BR-001/v2 active. A
faulty deployment selects an absent second path and explicitly permits initial
creation. The unchanged service legitimately initializes that file at v1. A
request for EUR 4,000 can therefore receive a different route. A historical
retry can even receive the same deterministic decision ID while being CREATED
in another ledger. Response equality alone does not prove historical replay.

The path-only control changes only `state_path`; it keeps the same request,
service source, catalogue and other faulty configuration fields. Recovery adds
separate fail-closed guards after that causal isolation. Test all three causal
hypotheses: threshold-code regression, a retry implementation defect, and wrong
state selection. Claims must cite the observed, stable event IDs in the review.

## Bounded recovery

Select `state/control/history.sqlite`, disable missing-state initialization,
require active `BR-001/v2`, and require the retained `rollout_anchor` key. The
anchor is a synthetic historical presence check, not an authenticated globally
unique database identifier. The owner gate also binds exact database bytes and
the preserved records. It rejects escaping and symlinked state paths.

Retain both original and incident ledgers. Gates run on new copies; they never
merge, overwrite or delete incident decisions. Incident-only rows remain
quarantined pending an explicit owner reconciliation decision. A separate copy
tests a fresh post-recovery request so the preserved ledger stays byte-identical.
Local restoration, reconciliation, and permanent-fix rollout are different
states. The local guard can pass while reconciliation and production rollout
remain unapproved. Keep the full causal log, raw process output and failed
experiments. Repeated runs require new output directories.

## Authority and observability

`PASS_INCIDENT_RECOVERY_REVIEW_ONLY` grants no production operation, release,
payment, real human acceptance, or incident-closure authority. CP07 T07-03 stays
pending and T07-04 blocked. CP10 concerns only its separate presentation release
rehearsal; CP11 review is not production migration approval.

Telemetry is standard-library JSON from fresh local Python processes, with
process IDs, timestamps, selected paths, source/configuration hashes, state
summaries and outcomes. It is not OpenTelemetry SDK, OTLP, exporter, or backend
execution. This owner-run harness is not an OS sandbox or an authentication
system for arbitrary untrusted code or real-world historical records.
