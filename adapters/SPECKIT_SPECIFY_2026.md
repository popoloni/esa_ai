# Spec Kit SDD adapter — documentation snapshot, 19 October 2026

Official: https://github.com/github/spec-kit/blob/main/README.md and https://github.com/github/spec-kit/blob/main/docs/reference/agentic-sdd.md

Install/initialize using exact pinned version after choosing your integration. Example documented at time of writing:

```bash
uv tool install specify-cli
specify init . --integration copilot
```

Inside your agent chat (NOT shell), invoke the integration-specific skill spelling. Copilot skills notation currently includes:

```text
/speckit-specify Explain the existing routing recommendation only.
  Use DISC-003/v1, SRC-POL-001 and the authority boundary.
  Do not modify routing, authorize payments, or claim validated ROI.
/speckit-clarify Focus on the invalid-amount and threshold-boundary cases.
/speckit-analyze
```

Verify the produced spec.md and any checklist manually against reader-side case vectors. `analyze` may require plan.md and tasks.md as well: use it at the appropriate later stage, not as a shortcut to requirements approval. Syntax and artifacts depend on pinned integration/release. No live Spec Kit execution is claimed.
