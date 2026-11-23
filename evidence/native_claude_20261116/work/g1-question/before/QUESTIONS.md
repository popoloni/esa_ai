# Operator questions before delegation (G1/I01)

Recorded by the AI operator of the 16 November 2026 native run, before any agent session
and before the supplied owner response was released.

1. `get_reservation` is specified only "for a reservation that exists". What must it
   return for an identifier that was never created: `None`, an exception, or an empty
   mapping? A caller cannot distinguish "absent" from a storage failure until this is decided.
2. Is a non-positive identifier (0, -1) the same case as an absent one, or a caller error?
