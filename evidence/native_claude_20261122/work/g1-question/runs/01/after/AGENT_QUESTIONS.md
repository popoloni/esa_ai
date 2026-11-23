# G1/I01 — agent questions before implementation

Stage: QUESTION_PENDING (per `READER_ENTRY.json`). Written before any owner response.
Sources read: `docs/G1-I01.md` (draft 2025-05-14), `docs/decisions/0001-storage.md`,
`booking.py` (public interface stubs), learner `QUESTIONS.md` (left unchanged).
No owner answer was requested or seen. Nothing in this file has been approved.

## Blocking question for the owner (needs authority)

> **Q1. When `get_reservation(path, reservation_id)` is called with a positive integer
> identifier that has no reservation in an initialised database, what must it do:
> return `None`, or raise an exception — and if it raises, which exception type
> (for example `KeyError`, `LookupError`, or a named domain exception exported from
> `booking.py`)?**

Why it blocks: the brief defines the read only "for a reservation that exists"
(G1-I01.md:19-22) and says it "intentionally leaves a decision open" (line 4). Both
answers are plausible and incompatible: a caller written for `None` silently
mis-handles a raise, and vice versa. A public test can observe this directly, and
it fixes the function's return type. This is the learner's question 1, made exact.

## Further questions (consequential, answer with Q1 if possible)

**Q2. Missing or uninitialised storage on read.** If `path` does not exist (or exists
but `init_db` was never called), must `get_reservation` fail without creating any
file, or may it create empty storage? If it fails, with which exception?
(Learner's question 2.) Note: "Reading does not modify records" (line 22) does not
settle whether creating an empty file is allowed. My proposed default, pending
the owner: fail, create nothing.

**Q3. `reserve` without prior `init_db`.** Must `reserve` work on a path where
`init_db` was not called (creating storage itself), or is `init_db` a precondition
whose violation surfaces as a propagated storage error? The brief says only that
`reserve` accepts a first request "in an empty database".

**Q4. Invalid identifier type/value on read.** For `reservation_id` that is `0`,
negative, a `bool`, or a string like `"1"`: same behavior as Q1 (not found), or a
`TypeError`/`ValueError`? Proposed default: treat non-positive ints as not found
(same as Q1); type checking deferred to G2 strict validation unless the owner says
otherwise.

**Q5. Mapping shape.** Is a plain `dict` required, or any `Mapping`? Must
`reservation_id` in the mapping be `int` (identical to `Outcome.reservation_id`)
while the other five are `str`? Proposed default: fresh `dict`, `int` id, `str` rest
— this follows from "values must equal the original request and returned
identifier" and should not need authority unless the owner disagrees.

## Recorded as out of scope (no question needed)

- Behavior for a second request, duplicate key, overlap, invalid fields, or replay:
  deferred to G2 (G1-I01.md:5-6, 43-49). G1 must not invent it.
- Request fingerprint / `request_hash`: explicitly not required (line 28).
- Internal table/column names: private (line 27; ADR lines 3-7).

## Observations on the workspace (evidence, not action)

- The brief cites `docs/contract.md` and the ADR cites `historical_tests/`; neither
  is present in this workspace. No `tests/` directory exists yet; the brief says
  the `clarify` step supplies the checks. I did not run any checks.
- `AGENTS.md` lists `booking.py`, `QUESTIONS.md`, `DOSSIER.md` as editable; this
  run's task restricts edits to `AGENT_QUESTIONS.md` and `AGENT_PLAN.md`. I followed
  the narrower task scope; `QUESTIONS.md`, `DOSSIER.md`, `booking.py` are unchanged.
