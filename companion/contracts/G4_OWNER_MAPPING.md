# G4-OD-01: owner mapping for this G3 lineage

Owner: fictional operations lead. Status: approved teaching decision.
Fictional case decision date: 2025-05-22. Applies to this G4 candidate only and
extends OPS-G4/v3 in `docs/contract.md`; every rule there still holds.
This is a supplied teaching response, not evidence that a human owner reviewed
your storage.

OPS-G4/v3 names three schema-3 representations. The retained G3 `booking.py` of
this lineage (SHA-256 `@BOOKING_SHA256@`) keeps its current reservations in
another one: table `@TABLE@`. @ORIGIN@

The owner recognizes that table, with exactly these columns in this order, as a
fourth current representation for this lineage:

`@SIGNATURE@`

| Role | Column |
|:--|:--|
@ROLE_ROWS@

`docs/G4-SCHEMA-MAP.json` records the same table, signature and roles for
programs. `diagnose` reads it from the `docs` folder next to `operations.py`
when it exists; candidates without it keep the three named representations.

- Match the complete recorded signature. The same table name with any other
  column list is unsupported.
- The mapped table is one more *current* representation. Refuse it alongside
  any named representation, as OPS-G4/v3 refuses any competing pair.
- Use the role columns for every query: identifier pairs, asset, interval and
  state. State values are those of RES-002: `active` and `cancelled`.
- Schema version 3 remains required. Do not repair, delete or initialize data.

This mapping does not certify any other database or a later change to
`booking.py`. If storage changes, ask again.
