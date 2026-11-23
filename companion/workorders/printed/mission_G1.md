**EDOD/1 work order mission_G1 — New capability.**

**Expect** — **outcome:** Commit the first reservation and retrieve its six public fields. **authority:** Workshop coordinator, G1/I01 + G1-OD-01 (teaching contract). **acceptance:** One valid request survives writer exit; missing-ID and missing-storage outcomes follow the owner decision.

**Delegate** — **editable_paths:** `booking.py`, `DOSSIER.md`. **protected_paths:** `docs/`, `tests/`, `READER_ENTRY.json`, `prior/`, `historical_tests/`. **budget:** 3 attempts / 25 implementation minutes; 15 s per check process; 0 external integration calls. **stop_conditions:** No supplied lookup decision; new replay or overlap policy. Protected inputs change or the declared attempt/time budget is spent.

**Observe** — **checks:** `g1.check`, `g1.continue` (commands below). **receipt_fields:** `candidate_sha256_before`, `groups`, `inputs_unchanged`, `verification_progress`, `human_acceptance`.

**Decide** — **owner:** Learner reviewer; Workshop coordinator for a changed rule. **object:** G1 candidate, identified bytes and its scoped handoff. **allowed_decisions:** ACCEPT, REJECT, ASK.
