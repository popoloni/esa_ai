# CP07: OpenAI Agents API and multi-agent adapter (not executed)

**Docs checked:** 2026-10-19. **Execution:** NO API session, subagent or managed harness run.

Current OpenAI Agents API documentation describes independent subagents with their own contexts and a coordinator. A *separate subagent* may still share the same environment/filesystem with its parent, depending on the configured runtime. It does not automatically provide isolated writable worktrees, independent acceptance evidence or owner approval.

The CP07 portable task model should be converted into runtime-specific messages and permissions only after selecting a supported runtime. Do not assume the same API fields exist in a local Codex CLI session or in every SDK. Use two subagents only for the bounded read-only investigations, and wait for an external human architecture decision before any writing task.

**Official references:**
- https://developers.openai.com/api/docs/guides/agents-api/multi-agent
- https://developers.openai.com/api/docs/guides/agents
