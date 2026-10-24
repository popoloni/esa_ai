# Choose a learning route

[Home](../README.md) · [Install and start](GETTING_STARTED.md) · [Reader navigation](README.md)

The companion has two primary routes. Both use the same learning loop: read the
authority, create a separate learner copy, observe the supplied initial state,
make a bounded change, run independent checks, review the evidence and preserve
the result. Choose by the system state you want to practise.

| | Brownfield Treasury laboratory | Greenfield Reservation Studio |
| --- | --- | --- |
| Reader goal | Safely change an existing system | Build the first reliable slice of a new system |
| Book placement | Numbered Laboratories 1–14 | Independent, unnumbered studio after Laboratory 14 |
| Starting authority | Existing intent, behavior, protected checks and chapter cards | RES-001/v1 contract, ADR and independent scenarios |
| Learner copy | `python3 -B reader_start.py new 1 --destination ../my_treasury_lab` | `python3 greenfield_studio/tools/scaffold.py ../my_first_reservations` |
| Entry record | `READER_ENTRY.json` identifies the chapter and supplied state | `READER_ENTRY.json` identifies the route and supplied state |
| Supplied initial state | Deliberately faulty Chapter 1 router | Deliberately incomplete `booking.py` |
| Expected first result | Seven cases: three pass, two fail and two error | Ten tests fail with `NotImplementedError` |
| Edit boundary | Only paths printed by `reader_start.py show N` | `booking.py`; preserve `docs/` and `tests/` |
| Candidate check | Commands printed by the current chapter card | `python3 -m unittest discover -s tests -v` |
| Reference boundary | Separate worked-example route; it does not repair or accept the candidate | Separate `check_reference.py`; it does not repair or accept the candidate |
| Continue | Preserve one cumulative copy through Chapters 1–14 | Treat the completed slice as brownfield before proposing v2 behavior |

## Shared prerequisites

Both routes require Python 3.10 or newer and use only the standard library for
their core exercises. The Brownfield Treasury route additionally requires Git
with `merge-tree --write-tree`; its `doctor` command checks this and repository
integrity. Neither route requires a model account, API key, external database,
Docker or third-party Python package.

Run commands below from the top-level checkout—the directory containing
`reader_start.py` and `greenfield_studio/`. Use a new destination outside the
checkout, and do not overwrite or repurpose a previous attempt.

## Brownfield: start from inherited behavior

```bash
python3 -B reader_start.py doctor
python3 -B reader_start.py show 1
python3 -B reader_start.py new 1 --destination ../my_treasury_lab
cd ../my_treasury_lab
python3 -B reader_start.py show 1
```

Continue only when `doctor` reports `PASS_PREREQUISITES_ONLY` with empty
`protected_findings` and `release_starter_findings`. Follow the Chapter 1 card,
retain the initial failing evidence, edit only its permitted path and preserve
the same study copy for later chapters. See [Getting started](GETTING_STARTED.md)
for the complete first exercise.

## Greenfield: start from an approved contract

```bash
python3 greenfield_studio/tools/scaffold.py ../my_first_reservations
cd ../my_first_reservations
python3 -m unittest discover -s tests -v
```

The initial failure is intentional. Read `docs/contract.md` and
`docs/decisions/0001-storage.md`, preserve `tests/`, and implement only
`booking.py`. When the candidate passes, review what the ten local SQLite tests
do and do not establish. See the [Greenfield Studio guide](../greenfield_studio/README.md)
for the complete exercise.

## Evidence means the same thing in both routes

A passing local check establishes only the stated synthetic contract under its
recorded conditions. It is not human acceptance, permission to deploy, proof of
learning outcomes or evidence of production security, reliability and scale.
Keep candidate evidence separate from reference evidence and record unresolved
decisions before continuing.
