# Greenfield Reservation Studio

[Home](../README.md) · [Choose a route](../navigation/STARTING_ROUTES.md) · [d16 alignment](../navigation/GREENFIELD_STUDIO_d16.md)

Build the first reliable slice of a new reservation system from an approved
contract. This is the independent, unnumbered Greenfield route in d16; it
complements but does not modify the 14 cumulative Brownfield Treasury
laboratories.

Like the Brownfield route, this exercise asks you to read the authority, create
a separate learner copy, observe the supplied initial state, make a bounded
change, run independent checks, review the evidence and preserve the result.

## 1. Check the prerequisites and authority

Use Python 3.10 or newer. The studio is offline and standard-library-only; its
SQLite database is local. It requires no Git feature, package installation,
model endpoint, API key, payment credential or real booking account.

Before generating a learner copy, read:

- `docs/contract.md` — RES-001/v1, the fictional owner's accepted behavior;
- `docs/decisions/0001-storage.md` — the bounded storage decision;
- `tests/test_booking.py` — independent scenarios derived from the contract.

There is no existing application, legacy behavior or inherited regression suite.
Do not read `reference/booking.py` before attempting the exercise.

## 2. Create one learner copy

From the top-level companion checkout—the directory containing
`reader_start.py` and `greenfield_studio/`—choose a new destination outside the
checkout:

```bash
python3 greenfield_studio/tools/scaffold.py ../my_first_reservations
cd ../my_first_reservations
```

The scaffold command refuses to overwrite an existing destination. Keep the
companion checkout unchanged and open `my_first_reservations` in your editor.
The generated `READER_ENTRY.json` records the route, release, supplied state and
acceptance boundary, while `README.md` keeps the learner steps with the copy.

## 3. Record the supplied initial state

```bash
python3 -m unittest discover -s tests -v
```

All ten tests initially encounter `NotImplementedError`; this is the intended
learner state, not a missing dependency. Preserve this result. Missing contract,
decision or test files are packaging problems and are not intended failures.

## 4. Implement within the boundary

Edit only `booking.py`. Implement `init_db` and `reserve` against RES-001/v1.
Preserve the supplied `docs/` and `tests/`; do not weaken tests or turn a new
product decision into an implementation assumption.

Run the candidate check after each bounded change:

```bash
python3 -m unittest discover -s tests -v
```

The target is ten passing local tests. Review the implementation and test output,
including half-open intervals, idempotency and concurrency, before treating the
candidate as technically complete under this synthetic contract.

## 5. Compare with the reference separately

Return to the top-level companion checkout and run:

```bash
python3 greenfield_studio/tools/check_reference.py
```

This scaffolds the packaged reference into an isolated temporary directory and
runs the same ten tests. A reference pass does not modify, repair or accept your
learner copy.

## 6. Understand the evidence boundary

The checks cover selected functional and concurrency behavior on one local
SQLite database file. They do not validate public deployment, real
authentication or authorization, production load, security hardening, backups,
compliance, human acceptance or learning outcomes. A live rollout requires
those missing boundaries plus independent review and an accountable decision.

## 7. Continue as brownfield work

Preserve the completed learner copy and its evidence. Classify a waiting-list,
cancellation or other proposed feature as a new product decision, write a
compatible second-version contract, and establish regression expectations
before changing code. Once the first slice exists, the next change is
brownfield work.
