# PILOT-013/v1: delayed handoff, retention and transfer

This is a usable proposed human-pilot protocol, not a completed study. Its
24-hour minimum delay is a teaching choice, not a validated optimum. The
RUBRIC-013/v1 rubric has four dimensions scored by humans from 0 to 3:
causal_discrimination, evidence_linkage, history_and_identity, and
limits_and_next_action. Totals are descriptive. No competence pass threshold,
rubric validity, reliability estimate or learning gain is inferred by code.

## Machine exercise

From the companion root:

```bash
python3 reader_side/tools/rehearse_transfer.py \
  --learning-session CP12_SESSION --output NEW_TRANSFER
python3 reader_side/tools/learning_gate.py \
  --transfer-session NEW_TRANSFER --output NEW_REVIEW
```

Use `--reference` on both commands for a separate protected worked example.
`learning_gate.py` also accepts `--unsafe-control`, `--scope-baseline FILE`,
and `--receipt prior/LEARNING_RESULT.json`. Current and reference evidence
cannot certify each other. Success is `PASS_LEARNING_PROTOCOL_REVIEW_ONLY`.
The rehearsal writes `TRANSFER_SESSION.json` (cp13-transfer-session/v1); the
gate writes `LEARNING_RESULT.json` (cp13-learning-review/v1).

## Owner-run human pilot

Choose pseudonymous role IDs; participant, both reviewers and coordinator must
be distinct. Owner state, including the HMAC key, must be outside public trial
artifacts. Real access control and owner execution enforce that separation;
local file layout alone does not authenticate humans or prove independence.
The participant must not already have seen the transfer worked example. This
book's open teaching fixtures are unsuitable for an unseen-transfer claim if
the participant has studied their solution. Record that limitation or use a
separately approved unseen case; do not silently relabel exposure.

```bash
python3 reader_side/tools/learning_pilot.py start \
  --transfer-session NEW_TRANSFER --owner-state NEW_OWNER_DIR \
  --trial-output NEW_PUBLIC_DIR --participant learner_01 \
  --reviewer reviewer_a --reviewer reviewer_b --coordinator coordinator_01 \
  --attest-no-prior-transfer-exposure
python3 reader_side/tools/learning_pilot.py submit-baseline \
  --owner-state NEW_OWNER_DIR --file immediate_explanation.md
python3 reader_side/tools/learning_pilot.py release-retention \
  --owner-state NEW_OWNER_DIR
python3 reader_side/tools/learning_pilot.py submit-retention \
  --owner-state NEW_OWNER_DIR --file delayed_retention.md
python3 reader_side/tools/learning_pilot.py release-transfer \
  --owner-state NEW_OWNER_DIR
python3 reader_side/tools/learning_pilot.py submit-transfer \
  --owner-state NEW_OWNER_DIR --file transfer_explanation.md
python3 reader_side/tools/learning_pilot.py score \
  --owner-state NEW_OWNER_DIR --reviewer reviewer_a --file reviewer_a.json
python3 reader_side/tools/learning_pilot.py score \
  --owner-state NEW_OWNER_DIR --reviewer reviewer_b --file reviewer_b.json
python3 reader_side/tools/learning_pilot.py adjudicate \
  --owner-state NEW_OWNER_DIR --file adjudication.json
python3 reader_side/tools/learning_pilot.py status --owner-state NEW_OWNER_DIR
```

The delay begins when the baseline explanation is committed. A premature
release fails without advancing the trial. The retention response is committed
before transfer materials are published. Explanations and raw forms are
preserved byte-for-byte; later phases cannot overwrite them. The owner-held
event chain binds content, session, rubric, roles, clocks and phase transitions.

The initial public packet contains CP12 learning evidence and an exact
`baseline_prompt.md` task, together with protocol and rubric records. It does
not contain the post-transfer KNOW-013 knowledge card. The card is released as
`team_knowledge.json` only after the transfer answer has been sealed, when the
review forms appear. Transfer observation files are withheld until the
retention answer is sealed; the worked recovery observations are not released
as transfer task material.

Real mode accepts no supplied timestamp or clock override. It checks elapsed
wall and monotonic time on the same Linux host/boot, with a conservative drift
limit. Restart, migration to another host, wall-clock jumps or integrity failure
invalidate continuation; preserve the old trial and arrange a new one. This is
not a portable trusted timestamp service or a defense against an owner who
controls the host, checker and key.
The status field `real_clock_delay_elapsed` reports only this local elapsed
interval. It does not establish human participation, resource compliance,
independence, retention or competence.

## Reviewer record contract

At AWAITING_REVIEWS the public trial contains blank forms in `review_forms/`.
These templates are immutable. Copy `review_forms/reviewer_a.json` and
`review_forms/reviewer_b.json` into separate working locations outside both
the public trial and owner-state trees, fill those copies, and pass the
external paths to `score --file`. Never edit a public template in place.
The first raw score remains owner-private until the second score is sealed.
Then both raw profiles are published together under `reviews/` and the public
`adjudication_form.json` template appears. To adjudicate, copy that template
outside both immutable trees, fill the copy, and pass its path to
`adjudicate --file`. The resulting separate record is `adjudication/raw.json`.
Each `cp13-independent-score/v1` form binds trial_id, reviewer_id, rubric_id,
rubric_sha256, transfer_session_sha256, and all three answer_sha256 values.
`ratings` maps baseline/retention/transfer to the four rubric dimensions;
`rationales` contains a human explanation for each task. `attestations` records
human_record, independent_scoring, and no_other_scores_seen. The tool validates
the declared fields, not their truth. Candidate-supplied scores are not read as
learning evidence. The two raw reviewer forms are separate immutable inputs.

The output lists both score profiles and per-dimension disagreements. Optional
`cp13-adjudication/v1` binds both raw review hashes, coordinator identity and a
new rationale/score profile. It appends a record; it never replaces the original
disagreement. Distinct IDs, declarations and HMACs are not human authentication.

## Synthetic calibration and limits

```bash
python3 reader_side/tools/learning_pilot.py calibrate \
  --transfer-session NEW_TRANSFER --output NEW_CALIBRATION
```

Only this protected synthetic path can inject fixed clock observations. It uses
fictional explanations and raters, including disagreement, and reports
SYNTHETIC_CALIBRATION. It cannot establish that 24 real hours elapsed or that
any human learned, retained or transferred a skill. Human trial and rubric
validity remain pending in automated delivery results. Real participant records
are operator-attested evidence requiring owner confirmation, not automated
competence certification.

CP07 stays pending/blocked; CP12 incident reconciliation stays pending. Nothing
here authorizes release, production recovery, payment or incident closure.
