**EDOD/1 work order mission_G4 — Persistent effect.**

**Expect** — **outcome:** Diagnose retained storage read-only and account for all attempts. **authority:** Operations lead, OPS-G4/v3 (teaching contract). **acceptance:** Read-only diagnosis recognizes the three explicitly documented G3 schema3 representations and refuses unknown/competing mappings. All attempts count toward accepted-outcome accounting.

**Delegate** — **editable_paths:** `operations.py`, `DOSSIER.md`. **protected_paths:** `docs/`, `tests/`, `READER_ENTRY.json`, `prior/`, `booking.py`, `g4_fixture.py`, `reference_g3.py`. **budget:** 3 attempts / 25 implementation minutes; 30 s per check process; 0 external integration calls. **stop_conditions:** Missing or unsupported storage, changing bytes, or a requested repair. Protected inputs change or the declared attempt/time budget is spent.

**Observe** — **checks:** `g4.check`, `g4.continue` (commands below). **receipt_fields:** `candidate_sha256_before`, `groups`, `inputs_unchanged`, `verification_progress`, `human_acceptance`.

**Decide** — **owner:** Learner reviewer; Operations lead for a changed rule. **object:** G4 candidate, identified bytes and its scoped handoff. **allowed_decisions:** ACCEPT, REJECT, ASK.
