**EDOD/1 work order mission_G2 — Persistent effect.**

**Expect** — **outcome:** Complete admission and replay while preserving stored G1 work. **authority:** Workshop coordinator, RES-001/v1 + G2-OD-01 + G2-OD-02 (teaching contract). **acceptance:** Identity, conflicts and migration preserve public fields/history for the three explicitly authorized G1 signatures; unknown mappings are refused.

**Delegate** — **editable_paths:** `booking.py`, `DOSSIER.md`. **protected_paths:** `docs/`, `tests/`, `READER_ENTRY.json`, `prior/`, `legacy_g1.py`, `legacy_g1_json.py`, `legacy_g1_recorded.py`. **budget:** 3 attempts / 40 implementation minutes; 30 s per check process; 0 external integration calls. **stop_conditions:** Ambiguous legacy identity, unknown schema or new recurring-series rule. Protected inputs change or the declared attempt/time budget is spent.

**Observe** — **checks:** `g2.check`, `g2.continue` (commands below). **receipt_fields:** `candidate_sha256_before`, `groups`, `inputs_unchanged`, `verification_progress`, `human_acceptance`.

**Decide** — **owner:** Learner reviewer; Workshop coordinator for a changed rule. **object:** G2 candidate, identified bytes and its scoped handoff. **allowed_decisions:** ACCEPT, REJECT, ASK.
