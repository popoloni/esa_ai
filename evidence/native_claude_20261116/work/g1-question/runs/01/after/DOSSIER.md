# G1 working note

Scope: G1/I01 first durable reservation and public read; final RES-001/v1 remains separate.

## Expected behavior before coding

Given an empty database, member `member-1`, asset `A`, 2025-05-14T09:00:00Z to
2025-05-14T10:00:00Z, key `key-1`: when the member reserves, the outcome is 201/confirmed,
a positive identifier, replayed False. When a separate process calls `get_reservation`
with that identifier, it returns exactly the six public fields with the request values.
Open: the result for an identifier that does not exist (see QUESTIONS.md).

## Proposal review

Candidate ID, ACCEPT/REJECT/ASK, reason, decisive observation.

## Change and attempts

Record the reason for the change and receipt filenames.

## Handoff

State what passed, what remains, and who decides next.
