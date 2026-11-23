# B1 working note

Scope: BR-001/v1 finite positive amounts and unchanged EUR 5,000 boundary; B1 str API.

## Expected behavior before coding

Given `assess("-Infinity")` (or "inf", "NaN", "sNaN", "0.00", "-0.01", "not-an-amount"),
when assessed, then REJECTED / INVALID_AMOUNT / BR-001/v1. Discriminating pair:
"4999.99" -> STANDARD_QUEUE, "5000.00" -> HUMAN_REVIEW. `assess(4000)` raises TypeError.

## Proposal review

- legacy-note-001 (threshold 10000, auto_approve): REJECT. Status "proposal", owner unknown;
  BR-001/v1 is approved and an approved rule is not overridden by a newer proposal.
  Decisive observation: docs/policy.json keeps threshold 5000.00.
- Stricter grammar (no exponent/underscore): ASK/not implemented. No owner decision exists;
  `1e3` and `4_000` still accepted (observed STANDARD_QUEUE), as B1-API/v1 states.

## Change and attempts

Before: 12 tests run, 7 failures + 3 errors (non-positive and Infinity not rejected, NaN/sNaN/
garbage raised InvalidOperation, non-str int/float not TypeError).
Change in src/treasury/routing.py: explicit `isinstance(str)` -> TypeError; `Decimal()` wrapped
in `except InvalidOperation` only; `is_finite()` and `<= 0` checked before the threshold
comparison. No catch-all, so unexpected errors propagate.
After: 12 tests OK (run via `python3 -c` with sys.path src + unittest discover -s tests;
PYTHONPATH= form needed approval and was not run). Ad hoc fault probe (mock Decimal raising
RuntimeError) -> RuntimeError propagated. No receipt files were produced. Tool commands used: ~10.

## Handoff

Passed in my runs: all 12 development checks and the probe. Not observed: the operator's
protected acceptance run; no human approval is claimed. Remaining: the owner must decide whether
a stricter monetary grammar is wanted; whitespace/sign forms are still accepted. Tests/docs
untouched; QUESTIONS.md was not created (not in this task's allowed edits).
