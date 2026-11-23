**EDOD/1 work order mission_B1 — Bounded repair.**

**Expect** — **outcome:** Repair finite-positive routing under the current string API. **authority:** Treasury policy owner and API maintainer, BR-001/v1 + B1-API/v1 (teaching contract). **acceptance:** Reject invalid amounts; below 5000 uses STANDARD_QUEUE, equality uses HUMAN_REVIEW; non-string callers raise TypeError and unexpected errors propagate.

**Delegate** — **editable_paths:** `src/treasury/routing.py`, `DOSSIER.md`. **protected_paths:** `docs/`, `tests/`, `READER_ENTRY.json`, `prior/`. **budget:** 3 attempts / 25 implementation minutes; 15 s per check process; 0 external integration calls. **stop_conditions:** Threshold, precision or API change lacks an owner decision. Protected inputs change or the declared attempt/time budget is spent.

**Observe** — **checks:** `b1.check`, `b1.continue` (commands below). **receipt_fields:** `candidate_sha256_before`, `groups`, `inputs_unchanged`, `verification_progress`, `human_acceptance`.

**Decide** — **owner:** Learner reviewer; Treasury policy owner and API maintainer for a changed rule. **object:** B1 candidate, identified bytes and its scoped handoff. **allowed_decisions:** ACCEPT, REJECT, ASK.
