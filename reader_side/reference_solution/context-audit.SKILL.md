---
name: context-audit
description: Use when preparing or reviewing Treasury engineering context packets, checking source provenance, validity, supersession and pending architecture decisions before delegating a change.
---
# Review a knowledge packet

1. Read the source catalogue and locate the current approved policy and reviewed specification.
2. Record source IDs and status. Treat `K-ADR-005` as a proposal requiring human review.
3. Exclude stale or untrusted source assertions from normative claims; report them as evidence of conflict only.
4. Use the owner-run `python reader_side/tools/knowledge_gate.py` for deterministic selected checks.
5. When a source changes, recompute affected claim dependencies and request human review.
6. Report limitations: a passing gate does not authorize a payment, a deployment or an architectural decision.

See `references/CASE_SOURCE_MAP.md` for the source-type inventory.
