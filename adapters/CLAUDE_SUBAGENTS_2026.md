# CP07: Claude Code subagent adapter (documentation example, not executed)

**Docs checked:** 2026-10-19. **Client execution:** NOT RUN.

A read-only research subagent can be represented as a project `.claude/agents/spec-investigator.md` file (refer to current version before using):

```markdown
---
name: spec-investigator
description: Inspect a bounded, source-qualified requirements task and report disagreements.
tools: Read, Glob, Grep
---
Review the task card T07-01 and the listed sources. Do not edit the project.
Distinguish source status, unknowns, and owner decisions. Report source locators.
```

The documented tool list and host permissions must actually be checked; this is not an OS filesystem sandbox. A subagent's separate context does not itself protect a shared project, nor does it make a second opinion independent of shared model assumptions. An agent team is a different feature from one subagent.

Do not delegate T07-04 until the technical owner explicitly resolves T07-03 and changes the plan version and writability policies. For agent teams use separate ownership, merge and reviewer accountability; do not assume concurrency is beneficial here.

**Official references:**
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/agent-teams
