# CP07: GitHub Copilot delegation adapter (documentation example, not executed)

**Documentation snapshot:** 2026-10-19. **Status:** no Copilot CLI or IDE session run in CP07.

The portable plan is `reader_side/reference_solution/delegation_plan.json`. It is **not** a Copilot-native plan format. A team may turn one READ_ONLY_AGENT card into a repository custom agent profile in `.github/agents/spec-investigator.agent.md`, after checking the current tool aliases:

```markdown
---
description: Explore a bounded specification question without changing repository files.
tools: ["read"]
include-custom-instructions: true
---
Use only task-card source references; report uncertainty and file/line citations. Do not edit.
```

The `include-custom-instructions` property is relevant to Copilot CLI custom agents **spawned as subagents**; without this opt-in such subagents need not receive repository instructions. Other Copilot surfaces differ. The model's compliance and actual tool restrictions are not verified by the file's presence. Do not paste this profile into a real workspace without verifying product/version compatibility and execution permissions.

The human technical owner still must accept/reject `ADR-005`. A Copilot subagent summarizing tests cannot approve architecture or release. The CP07 `scope_guard.py` is run from separately controlled CI/owner context, not an enforceable Copilot policy.

**Official references:**
- https://docs.github.com/en/copilot/reference/custom-agents-configuration
- https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli
