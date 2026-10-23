# Chapter 13: Grow skills, knowledge and team governance

CP13 continues the same Treasury laboratory. Its process evidence is real local
Python/SQLite execution using the unchanged CP11 PolicyStore and CP12 service.
Its people, answers, scores and elapsed intervals in automated calibration are
explicitly synthetic. No human learning result or rubric validation is claimed.

Run commands from this `companion/` directory. Python's standard library and the
local Git already required by the cumulative lab are sufficient; no model,
account, network, OpenTelemetry SDK or external telemetry service is used.

## The new transfer case

CP12 selected the wrong state path. TRANSFER-013 keeps the correct existing
ledger selected, then records a synthetic activation from BR-001/v2 back to
BR-001/v1. A new EUR 4,000 request is created under v1 and enters STANDARD_QUEUE.
An earlier request originally decided under v2 still replays HUMAN_REVIEW.
The same source with an explicit v2 selection remains correct. The safe CP12
configuration rejects the unexpected active policy; changing the path alone
does not repair this cause.

Recovery operates on a new copy, restores active v2, verifies fresh requests,
historical retries and recomputation, and preserves the complete earlier rows
and audit prefix. The fault ledger and original CP12 evidence stay intact.
These observations support a bounded synthetic diagnosis and local recovery
review. They do not authorize production operations or reconciliation.

## Two editable records

WO-013 permits only:

- `repo/engineering/learning/transfer_review.json`
- `repo/engineering/learning/team_knowledge.json`

The supplied records intentionally repeat the earlier wrong-path diagnosis,
omit claim dependencies and overclaim authority. Protected unsafe controls
remain faulty after learner repairs. The reference records are under
`reader_side/reference_solution/ch13/`. All prompts, rubric, protocol,
calibration data, checks and earlier source remain owner-controlled.

The review names the competing hypotheses and actual T/U observations. The
knowledge card is a proposed, owned, versioned record with named source/evidence
dependencies and revision triggers. It is practical team guidance, not an
installed personal skill. Changing a bound dependency invalidates the receipt
and identifies affected knowledge claims; no generated card becomes policy or
delegated authority merely because a gate passes.

## Current-candidate exercise

Complete the earlier current CP01–CP09, CP11 and CP12 candidates first. Keep a
passing current CP12 incident session and use new paths for every output:

```bash
python3 reader_side/tools/scope_guard.py --chapter CP13 \
  --capture reader_side/evidence/CP13_EDIT_BASELINE.json
python3 reader_side/tools/rehearse_transfer.py \
  --learning-session reader_side/evidence/CP12_CURRENT \
  --output reader_side/evidence/CP13_TRANSFER

# Review the evidence and edit only the two CP13 candidates.
python3 reader_side/tools/learning_gate.py \
  --transfer-session reader_side/evidence/CP13_TRANSFER \
  --scope-baseline reader_side/evidence/CP13_EDIT_BASELINE.json \
  --output reader_side/evidence/CP13_REVIEW
python3 reader_side/tools/learning_gate.py \
  --transfer-session reader_side/evidence/CP13_TRANSFER \
  --receipt reader_side/evidence/CP13_REVIEW/LEARNING_RESULT.json \
  --output reader_side/evidence/CP13_RECEIPT_RECHECK
```

The rehearsal reports `TRANSFER_REPRODUCED_REVIEW_ONLY`. A passing review is
`PASS_LEARNING_PROTOCOL_REVIEW_ONLY`. The report distinguishes machine-checked
transfer evidence, dependency review and synthetic protocol calibration from
`human_delay_trial: PENDING`, `rubric_validity: PENDING_HUMAN_VALIDATION`, and
`human_competence: NOT_ESTABLISHED_BY_AUTOMATION`.

The gate binds selected source, prior artifacts, rubric, protocol, protected
manifest, process logs and every retained SQLite/evidence file by SHA-256.
`--receipt` requires the earlier passing result and its calibration evidence to
remain unchanged. These local receipts are integrity records under owner
control, not independently authenticated attestations. A baseline captured
before edits establishes actual CP13 edit scope; omitting it cannot do so.

To require the current cumulative machine workflow:

```bash
python3 reader_side/tools/run_checks.py \
  --incident-rehearsal reader_side/evidence/CP12_CURRENT \
  --transfer-session reader_side/evidence/CP13_TRANSFER \
  --require-learning --output reader_side/evidence/CP13_COMBINED.json
```

The nominated CP12 session must be the actual learning session bound by CP13.
Current and protected-reference evidence cannot certify one another. CP10
release remains separate and `NOT_RUN` unless nominated; modifying either CP13
candidate also makes an earlier CP10 source receipt stale. CP10's synthetic
presentation-only authorization never grants learning, policy-v2 or incident
authority.

For the protected worked example, create a fresh CP12 reference session, use
`rehearse_transfer.py --reference`, then `learning_gate.py --reference` with new
output directories. `--unsafe-control` evaluates the stable faulty CP13 records
against that reference transfer session. It must fail after current repairs.

## Proposed delayed human pilot

Read `reader_side/learning/PROTOCOL.md` for the full command sequence. Start a
new owner-run trial with participant, two reviewer and coordinator IDs. The
initial public packet contains CP12 learning evidence, the protocol/rubric and
an exact `baseline_prompt.md`. Commit the immediate answer, then wait at least
the declared 24 hours. This interval is a local teaching choice, not a validated
optimal delay. Each prompt asks for actual resources, assistance, deviations
and prior exposure in the retained raw answer.

The owner tool releases the retention prompt only after both real wall-clock
and monotonic elapsed time satisfy the interval on the same Linux host/boot.
It accepts no user timestamp or clock override. Restart, host change, clock
discontinuity or record corruption blocks continuation; preserve the trial and
arrange a new one. `real_clock_delay_elapsed` concerns that local interval, not
human participation. It is not a portable timestamp service or protection
against an owner controlling the host and key.

Seal the retention answer before releasing transfer observations. The latter
contain T01–T07 fault observations, not the U recovery worked solution. KNOW-013
is withheld until the transfer answer is sealed. The tool preserves original
answer bytes and binds task/session/rubric identities.

At AWAITING_REVIEWS, copy the blank forms from `review_forms/` outside both the
public and owner trees before editing. Two reviewers separately rate the three
answers on four provisional 0–3 dimensions and provide task rationales. The
first raw score stays owner-private until the second seals; then both appear
together with their disagreement. The public `adjudication_form.json` appears
only then. Copy it outside both trees, fill it, and submit the external path.
Adjudication is an additional `adjudication/raw.json`; original profiles remain.
No total is a competence pass threshold, and the tool does not grade prose.

The owner HMAC key and event chain stay outside public artifacts. Use actual
access controls and owner execution to enforce reviewer/exposure separation.
IDs, signatures and attestations do not authenticate people, demonstrate
independent judgment or verify resource compliance. The book's open worked
solution makes an unseen-transfer claim unsuitable for a reader who studied
it. Real records remain operator-attested and require owner confirmation;
rubric validity and learning inferences need an actual human pilot.

## Synthetic calibration and reproducible validation

```bash
python3 reader_side/tools/learning_pilot.py calibrate \
  --transfer-session reader_side/evidence/CP13_TRANSFER \
  --output reader_side/evidence/CP13_CALIBRATION
```

`PASS_SYNTHETIC_CALIBRATION_ONLY` checks chronology, withheld material,
independent raw-record handling, disagreement and additive adjudication with
protected fictional answers/raters and fixed synthetic clocks. Its owner key
is temporary and absent from outputs. The completed record remains explicitly
synthetic; no human waited or was assessed by this automated check.

From the book-package root, `python3 scripts/validate_chapter13_lab.py` uses a
new default `build/chapter13_validation` directory. For a later run, provide
`--output NEW_PATH`; prior evidence is never silently overwritten. It repairs
only disposable copies, exercises current/reference/unsafe gates, changed
sources and evidence, protected inputs, actual scopes, pilot boundaries and
the shared current workflow. It records observed counts and original-source
preservation. Scenario checks are not added to the unit-test count.

CP07's human architecture decision stays pending and T07-04 blocked. Incident
reconciliation stays pending. No local protocol status closes an incident,
releases software, pays money or certifies a person's competence.
