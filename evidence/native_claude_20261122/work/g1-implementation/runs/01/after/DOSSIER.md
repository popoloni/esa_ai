# G1 working note

Scope: G1/I01 first durable reservation and public read; final RES-001/v1 remains separate.

## Expected behavior before coding

Sources read: AGENTS.md, docs/G1-I01.md, docs/G1-OD-01.md, docs/contract.md,
docs/decisions/0001-storage.md, tests/*, historical_tests/*, READER_ENTRY.json.
No conflict between documents found. `G1-I01.md` governs G1; `contract.md` (RES-001/v1)
rules (validation, overlap, replay, concurrency) are G2 and not implemented.

Outcome: `reserve` commits one row and returns `201/confirmed`; `get_reservation`
returns the six public fields, `None` for an unknown id in an initialised database,
and raises `sqlite3.OperationalError` without creating a file when the path is missing.

Discriminating example:
Given an empty DB, member `member-1`, asset `A`, 2025-05-14T09:00:00Z–10:00:00Z, key `key-1`,
When the member reserves, Then `Outcome(201, "confirmed", n>0, False)`; and from a new
process `get_reservation(p, n)` equals the six request fields, `get_reservation(p, 999)`
is `None`, and `get_reservation(<missing path>, 1)` raises `OperationalError` leaving no file.

## Proposal review

The earlier AGENT_PLAN.md / AGENT_QUESTIONS.md are unapproved proposals. Their Q1/Q2 are
now answered by G1-OD-01 (None; OperationalError, no file). Their Q3 (reserve without
init_db), Q4 (non-positive/non-int ids) and Q5 (dict shape) were not decided by the owner;
I did not invent policy: tests always call `init_db` first, and a non-positive id simply
finds no row (`None`, as the readonly test requires for -77). Q3/Q4 remain unconfirmed.

## Change and attempts

Reason: all 6 G1 checks raised NotImplementedError (reproduced before editing).
Changed only `booking.py` (and this file). Corrections explained:
- `init_db`: `CREATE TABLE IF NOT EXISTS`, one private table; keeps existing data.
- `reserve`: parameterised INSERT inside a `with conn` transaction; Outcome is built only
  after commit; sqlite errors propagate.
- `get_reservation`: `file:` URI from `Path.resolve().as_uri()` + `?mode=ro`, parameterised
  SELECT, fresh dict; no row -> `None`.
No validation, overlap, replay or locking was added (G2).

Commands (cwd = workspace; `python3 -B` to avoid writing bytecode):
1. `python3 -I -m unittest tests.test_g1_slice ...` -> import error (no `tests` package, `-I`
   drops cwd); not an implementation result.
2. `python3 -B -m unittest discover -s tests -p 'test_g1_[sr]*.py'` before: 6 errors
   (NotImplementedError); after: Ran 6, OK.
3. `... -p 'test_g1_full_api.py'` after: Ran 10, 7 failures (expected, G2 scope: overlap,
   replay, changed key, validation, concurrency); 3 pass.
4. `python3 -B -m unittest discover -s historical_tests` after: Ran 10, 7 failures (same G2 set).
5. Separate-process probe (scratchpad DB): write printed `201/confirmed id=1`; a new process
   read the six fields correctly and `None` for id 999.

## Handoff

Passed (my own feedback runs): 4 slice + 2 read-only checks. Not claimed: protected
acceptance, human approval — the operator records those. Remaining: full-contract and
historical diagnostics fail by design until G2; `reserve` before `init_db` is unspecified
(a plain connect would create an empty file, then fail on the missing table); concurrency and
duplicate behavior untested; no crash-recovery claim. Next decision belongs to the operator/owner.
