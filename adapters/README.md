# Harness adapter notes — researched October 19, 2026

[Home](../README.md) · [Core setup](../navigation/GETTING_STARTED.md) · [Optional practice](../practice/README.md)

## Optional integration reference

These are documentation notes, not installable adapters or prerequisites for the core lab. Consult only the notes for a tool you have chosen to explore. Their research date and unobserved-client limitations still apply.

| Topic | Notes |
| --- | --- |
| Specification workflows | [Spec Kit specify](SPECKIT_SPECIFY_2026.md) · [Spec Kit assess](SPECKIT_ASSESS_2026.md) · [OpenSpec explore](OPENSPEC_EXPLORE_2026.md) · [OpenSpec delta](OPENSPEC_DELTA_2026.md) · [Kiro requirements](KIRO_REQUIREMENTS_2026.md) · [BMAD boundary](BMAD_BOUNDARY_2026.md) |
| Design and planning | [Architecture review](ARCHITECTURE_REVIEW_PROMPT_2026.md) · [Kiro design](KIRO_DESIGN_FIRST_2026.md) · [Copilot plan](COPILOT_PLAN_2026.md) |
| Delegation and coordination | [Copilot delegation](COPILOT_DELEGATION_2026.md) · [Claude subagents](CLAUDE_SUBAGENTS_2026.md) · [OpenAI multi-agent notes](OPENAI_AGENTS_MULTIAGENT_2026.md) · [Git worktrees](GIT_WORKTREES_2026.md) |
| External interfaces | [MCP](MCP_2026.md) · [Issues and Atlassian](ISSUES_AND_ATLASSIAN_2026.md) |

## Instruction-file projections

The shared project instruction is `repo/AGENTS.md`. Different harnesses discover additional files differently. The projection script creates small dated integration files; it does not imply that all of them were exercised in a live authenticated client.

For the edition's actual installed-client tutorial, start with
[`practice/native_client/README.md`](../practice/native_client/README.md).
That OpenCode 1.19.3 route retains its own configuration, model identity and
native actions. It uses a narrowly scoped configuration for the Chapter 1
repair. The five projections below remain their separately dated examples;
the OpenCode observation does not change their unobserved status.

| Harness | Current official anchor | Projection | Live validation |
| --- | --- | --- | --- |
| GitHub Copilot | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md`; skills in `.github/skills` or `.agents/skills` | `copilot` | NOT RUN |
| Claude Code | Project `AGENTS.md` now documented; `.claude/rules/*.md` with `paths`; `.claude/skills/*/SKILL.md` | `claude` | NOT RUN |
| Cursor | `.cursor/rules/*.mdc` with `globs`/`alwaysApply`, `AGENTS.md` alternative | `cursor` | NOT RUN |
| Codex | `AGENTS.md` and `.agents/skills/*/SKILL.md` | `codex` | NOT RUN |
| Kiro | `.kiro/steering/*.md` and `AGENTS.md` | `kiro` | NOT RUN |

**Critical limitation:** a repo instruction is not a filesystem ACL, approval rule, or sandbox. Client settings and OS controls must be configured and separately verified. Also check if your chosen client already loads the shared `AGENTS.md`, to avoid divergent/duplicated instructions.

## Sources

- GitHub Copilot: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- Copilot skills: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- Claude project memory: https://code.claude.com/docs/en/memory
- Claude skills: https://code.claude.com/docs/en/skills
- Cursor: https://cursor.com/docs/rules
- Codex: https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex
- Kiro: https://kiro.dev/docs/steering/
- Agent Skills spec: https://agentskills.io/specification
