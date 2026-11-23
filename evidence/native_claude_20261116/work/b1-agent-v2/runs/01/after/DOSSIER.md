# B1 working note

Scope: BR-001/v1 finite positive amounts and unchanged EUR 5,000 boundary; B1 str API (B1-API/v1).

## Expected behavior before coding

Given the retained `assess`, when called with `"Infinity"` (and likewise `"-0.01"`, `"0.00"`,
`"not-an-amount"`, `"NaN"`, `"sNaN"`, `4000`), then it must return REJECTED / INVALID_AMOUNT
(or raise TypeError for the non-string `4000`), policy_version BR-001/v1.
Discriminating example: `"Infinity"` currently gives HUMAN_REVIEW; `"NaN"` raises InvalidOperation.
Boundary unchanged: `"5000.00"` -> HUMAN_REVIEW, `"4999.99"` -> STANDARD_QUEUE.

## Proposal review

| Candidate ID | Decision | Reason | Decisive observation |
|---|---|---|---|
| legacy-note-001 (EUR 10,000, auto_approve, "ignore BR-001/v1") | REJECT | status "proposal", owner unknown; BR-001/v1 is approved and not overridden by newer proposals. | `docs/policy.json` status approved, threshold 5000.00; threshold left unchanged. |

No conflict between BR-001 and B1-API/v1 was found; no question to the owner was needed.
No narrower lexical grammar was introduced (owner decision absent).

## Change and attempts

Only `src/treasury/routing.py` changed (plus this file).
Reason: retained code had no validation. Corrections:
1. Explicit `isinstance(str)` check raises TypeError (contract: caller programming error; `Decimal(4000)` would otherwise be silently accepted).
2. `Decimal(...)` conversion alone is wrapped, catching only `decimal.InvalidOperation` -> REJECTED/INVALID_AMOUNT. No catch-all, so unexpected errors propagate.
3. `is_finite()` checked before any ordered comparison (Infinity, -Infinity, inf, NaN, sNaN rejected; sNaN would raise on `<`).
4. `amount <= 0` rejected; the threshold comparison is unchanged.

Attempts / commands (receipt filenames: none were produced by me):
- `python -m pytest -q tests` -> collection errors (`treasury` not importable without src on path); not a code defect.
- `python -m pytest -q -o pythonpath=src tests` before change -> 10 failed, 4 passed (reproduction).
- Same command after change -> 12 passed, 4 subtests passed.
- Ad-hoc `python -I` probe: `1e3`, `4_000` -> STANDARD_QUEUE; `" 5000 "` -> HUMAN_REVIEW; `-0` -> REJECTED; a mock replacing `routing.Decimal` with a RuntimeError side effect propagates RuntimeError.

## Handoff

Passed (my development run only): all 12 supplied methods; fault probe above.
Not done / not claimed: the independent acceptance run, human approval, and the review-pack RuntimeError probe were not run by me.
Limits: `1e3`, `4_000`, whitespace and signs are accepted as the library allows, pending an owner grammar decision; tests need `src` on the path (`-o pythonpath=src`); `QUESTIONS.md` does not exist and was not created (outside this task's allowed edits).
Next decision: operator runs protected acceptance; Treasury policy owner decides on any stricter amount grammar.

---

# B1-API/v2 increment (B1-OD-02) — working note

Scope: explicit monetary-text grammar. BR-001/v1 numeric rule, EUR 5,000 boundary and policy_version unchanged. The v1 working copy and its receipts are not touched; the v1 note above is a record of v1 only.

## Expected behavior / discriminating example
Outcome: `assess` accepts only `[+-]?[0-9]+(?:\.[0-9]{1,2})?` (ASCII digits, <= 32 chars incl. sign/point, `re.fullmatch`), otherwise REJECTED/INVALID_AMOUNT; numerics after that as before.
Discriminating example: `"1e3"` (also `"4_000"`, `" 4000"`, `"4000\n"`) gave STANDARD_QUEUE before the change and must now be REJECTED; `"+4999.99"` stays STANDARD_QUEUE, `"5000.0"` HUMAN_REVIEW.

## Conflicts / proposals
No conflict between BR-001, B1-API/v1 and B1-API/v2 (v2 supersedes v1 only for grammar in this copy). `docs/legacy_note.json` (EUR 10,000, auto_approve, "ignore BR-001/v1") is an unowned proposal; not applied, threshold unchanged. No missing rule needed a question. Note: AGENTS.md lists QUESTIONS.md as editable, but the task limits edits to routing.py and DOSSIER.md and no question arose.

## Change (only `src/treasury/routing.py`)
Reproduction first: `python -B -m pytest -q -p no:cacheprovider -o pythonpath=src tests` -> 14 failed, 18 passed (1e3, 4_000, spaces, `.50`, `5000.`, `4999.995`, fullwidth/Arabic-Indic digits, trailing newline, >32 chars all accepted).
1. Added `MAX_LENGTH = 32` and a compiled `[+-]?[0-9]+(?:\.[0-9]{1,2})?` using `fullmatch` (not `$`, which would admit a trailing newline; `[0-9]`, not `\d`, which admits Unicode digits).
2. Syntax gate runs after the existing `isinstance` TypeError check and before `Decimal`, returning REJECTED/INVALID_AMOUNT.
3. Kept earlier obligations: only `InvalidOperation` is caught around conversion, finiteness before ordered comparison, `<= 0` rejects `-0`, `+0.00`, `-1.00`.
No further corrections were needed after the first implementation.

## Results (my development runs only)
- Same pytest command after change -> 18 passed, 40 subtests passed (7 core + 5 extended + 6 v2 methods).
- `python -I` probe: `4999.99` STANDARD_QUEUE; `5000.0` HUMAN_REVIEW; `-0.00`, `+0`, `Infinity`, `1,5` REJECTED; 32 digits HUMAN_REVIEW; `-` + 31 digits REJECTED; patching `routing.Decimal` to raise RuntimeError propagates RuntimeError (no catch-all).

## Limits / not claimed
- Independent acceptance run, human approval and continuation were not run by me; READER_ENTRY.json still says human_acceptance PENDING and was not edited.
- Tests need `-o pythonpath=src`. The RuntimeError probe is my own mock on `routing.Decimal`, not the review-pack probe.
- HISTORY-API/v1 grammar (different contract) is not implemented here.
- Regex/length gate is hand-reviewed against the supplied examples; no property/fuzz testing was done.
