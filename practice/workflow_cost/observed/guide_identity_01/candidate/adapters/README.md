# Harness adapter notes — researched October 19, 2026

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
