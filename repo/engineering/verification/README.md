# Chapter 9 editable wrapper exercise

Editable student files for this task: `candidate.py` and `review.json` only. The intentionally faulty starter must be rejected by the reader-side gate. Repair these two files without changing the independent oracle, protected unsafe fixture, reviewer checks, routing policy or earlier chapters' code.

This wrapper exercise and the cross-chapter bridge have different subjects. The wrapper exercise verifies `propose_explanation`; the bridge independently checks the actual Chapter 8 `build_explanation` output, its presentation label and the corresponding evidence receipts. A passing wrapper reference does not prove that the Chapter 8 candidate is correct.

Run the owner-side commands from the unified `companion/` directory. Use `verification_gate.py --scope-baseline PATH` with the owner-created before-edit baseline to check the actual CP09 diff. A valid review stops at `READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED`, with `release_authorized: false` and pending human decisions intact.

The gate executes known educational fixtures locally. It is not an operating-system sandbox or production acceptance authority.
