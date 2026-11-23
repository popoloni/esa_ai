**EDOD/1 work order mission_B4 — Persistent effect.**

**Expect** — **outcome:** Diagnose the selected ledger and propose a bounded restoration. **authority:** Service operations lead, OPS-B4/v2 (teaching contract). **acceptance:** Compare actual and expected path, policy and anchor read-only; preserve both ledgers; leave reconciliation and production approval pending. The structured proposal includes restore_configuration_to with the resolved expected path; it does not perform or authorize restoration.

**Delegate** — **editable_paths:** `incident.py`, `DOSSIER.md`. **protected_paths:** `docs/`, `tests/`, `READER_ENTRY.json`, `prior/`, `ledger.py`, `routing.py`, `operations.py`. **budget:** 3 attempts / 30 implementation minutes; 30 s per check process; 0 external integration calls. **stop_conditions:** Missing ledger, changing evidence or requested record reconciliation. Protected inputs change or the declared attempt/time budget is spent.

**Observe** — **checks:** `b4.check`, `b4.continue` (commands below). **receipt_fields:** `candidate_sha256_before`, `groups`, `inputs_unchanged`, `verification_progress`, `human_acceptance`.

**Decide** — **owner:** Learner reviewer; Service operations lead for a changed rule. **object:** B4 candidate, identified bytes and its scoped handoff. **allowed_decisions:** ACCEPT, REJECT, ASK.
