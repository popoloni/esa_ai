**EDOD/1 work order mission_G3 — Persistent effect.**

**Expect** — **outcome:** Cancel atomically without changing the historical reservation interface. **authority:** Workshop coordinator, RES-002/v1 (teaching contract). **acceptance:** Owner/version guards preserve refused state; successful cancellation increments once; old replay retains the original reservation.

**Delegate** — **editable_paths:** `booking.py`, `DOSSIER.md`. **protected_paths:** `docs/`, `tests/`, `READER_ENTRY.json`, `prior/`, `legacy_booking.py`. **budget:** 3 attempts / 30 implementation minutes; 30 s per check process; 0 external integration calls. **stop_conditions:** Refund, deletion or staff-override policy is required. Protected inputs change or the declared attempt/time budget is spent.

**Observe** — **checks:** `g3.check`, `g3.continue` (commands below). **receipt_fields:** `candidate_sha256_before`, `groups`, `inputs_unchanged`, `verification_progress`, `human_acceptance`.

**Decide** — **owner:** Learner reviewer; Workshop coordinator for a changed rule. **object:** G3 candidate, identified bytes and its scoped handoff. **allowed_decisions:** ACCEPT, REJECT, ASK.
