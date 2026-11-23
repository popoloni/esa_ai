# Agent questions before implementation (G1/I01)

Sources read: `docs/G1-I01.md`, `docs/decisions/0001-storage.md`, `booking.py` (interface stubs), learner `QUESTIONS.md` (left unchanged).
No owner response was available or sought. Nothing was implemented or run.

## Blocking question (needs the owner)

**Q1. What must `get_reservation(path, reservation_id)` do for an identifier that does not exist?**
Options: (a) return `None`; (b) raise a specific exception (which type?); (c) return an empty mapping.
Why it blocks: the brief only defines reads "for a reservation that exists". Callers can't tell "absent" from a storage failure, and the brief says storage failures must propagate. This is the learner's Q1; I agree it is the most consequential gap.

## Further questions (can follow the same owner response)

2. Non-positive or non-integer identifiers (0, -1, "1"): same as absent, or a caller error (`ValueError`/`TypeError`)? (Learner Q2.)
3. `reserve` on a path where `init_db` was never called: should it create storage implicitly, or raise?
4. Calling `init_db` again must preserve data. Confirm that is the only G1 guarantee about re-init.
5. Scope edges the brief assigns to G2: a second `reserve` in a non-empty database (same key, same member, overlapping interval), and invalid input (empty or over-128-character ids, non-positive or over-24h interval). Should G1 leave these unspecified (implementation may behave arbitrarily), or must it raise an explicit "not supported in G1" error? I will not add validation or replay logic unless told to.
6. Return type of `get_reservation`: is a plain `dict` acceptable as the "fresh mapping", with `reservation_id` as `int`?

## Acceptance examples (proposed, to confirm after the owner answer)

A1. Given an empty database, `member-1`, asset `A`, 2025-05-14T09:00:00Z to 10:00:00Z, key `key-1`, when `reserve` is called, then it returns `Outcome(201, "confirmed", <int > 0>, False)`.
A2. Given A1 committed, when a new process calls `get_reservation(path, id)`, then it gets exactly the six fields equal to the request and the returned id.
A3. Given identifiers containing quotes (`o'brien`, `A"1`, `x'); DROP TABLE t;--`), when reserved and read back, then values round-trip unchanged and storage is intact.
A4. Given an existing reservation, when `get_reservation` is called twice, then the returned mappings are independent (mutating one doesn't affect the other) and records are unchanged.
A5. Given a committed reservation, when `init_db` is called again, then the reservation is still readable.
A6. Given an unknown id, when `get_reservation` is called, then the result is **pending Q1**.
A7. Given an unwritable or corrupt storage path, when `reserve` is called, then the storage exception propagates and no `201` is returned.
