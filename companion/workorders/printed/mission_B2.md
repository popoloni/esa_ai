**EDOD/1 work order mission_B2 — New capability.**

**Expect** — **outcome:** Classify a bounded local batch with attributable attempts. **authority:** Treasury service owner, INTAKE/v1 (teaching contract). **acceptance:** Preflight duplicate IDs before calls; cap attempts; validate returned identity/classification; preserve failed attempts and original errors.

**Delegate** — **editable_paths:** `intake.py`, `DOSSIER.md`. **protected_paths:** `docs/`, `tests/`, `READER_ENTRY.json`, `prior/`, `routing.py`. **budget:** 3 attempts / 30 implementation minutes; 30 s per check process; 0 external integration calls. **stop_conditions:** Provider blocks, response violates its protocol, or invocation budget is exhausted. Protected inputs change or the declared attempt/time budget is spent.

**Observe** — **checks:** `b2.check`, `b2.continue` (commands below). **receipt_fields:** `candidate_sha256_before`, `groups`, `inputs_unchanged`, `verification_progress`, `human_acceptance`.

**Decide** — **owner:** Learner reviewer; Treasury service owner for a changed rule. **object:** B2 candidate, identified bytes and its scoped handoff. **allowed_decisions:** ACCEPT, REJECT, ASK.
