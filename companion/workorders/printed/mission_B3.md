**EDOD/1 work order mission_B3 — Persistent effect.**

**Expect** — **outcome:** Preserve recorded decisions through policy change and migration. **authority:** Treasury policy owner and ledger maintainer, HISTORY-API/v1 + MIGRATION/v1 (teaching contract). **acceptance:** Replay keeps the saved answer; conflicts preserve history; reevaluation creates a linked ID; migration requires original evidence and commits atomically.

**Delegate** — **editable_paths:** `ledger.py`, `DOSSIER.md`. **protected_paths:** `docs/`, `tests/`, `READER_ENTRY.json`, `prior/`, `routing.py`. **budget:** 3 attempts / 40 implementation minutes; 30 s per check process; 0 external integration calls. **stop_conditions:** Missing historical provenance, conflicting identity or unavailable policy mapping. Protected inputs change or the declared attempt/time budget is spent.

**Observe** — **checks:** `b3.check`, `b3.continue` (commands below). **receipt_fields:** `candidate_sha256_before`, `groups`, `inputs_unchanged`, `verification_progress`, `human_acceptance`.

**Decide** — **owner:** Learner reviewer; Treasury policy owner and ledger maintainer for a changed rule. **object:** B3 candidate, identified bytes and its scoped handoff. **allowed_decisions:** ACCEPT, REJECT, ASK.
