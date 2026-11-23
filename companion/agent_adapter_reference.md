# EDOD and current agent tools

Documentation snapshot: **3 November 2026**. This is a mapping from an
engineering obligation to a product mechanism. It records documentation checks,
not successful execution of these clients. Use the installed client's version
and help output when recording a real run.

| Primitive | EDOD role | Observation to retain | Boundary |
|:--|:--|:--|:--|
| Codex or OpenCode `AGENTS.md`; Claude Code `CLAUDE.md` | Expect / Delegate: supply project instructions | Effective instruction paths and content hashes; a contract-resolving probe | Instructions do not make protected files unwritable. Discovery and precedence differ by client. |
| Skill | Delegate: load a reusable procedure | Skill identity, version and actual invocation | Loading instructions does not prove that each step ran. |
| Lifecycle hook | Observe / control a transition | Matched event, hook command, exit status and failure handling | A hook covers its configured event and tools. It is not a complete filesystem boundary. |
| Tool permission and OS sandbox | Delegate: constrain capabilities | Effective permissions and a denied-action probe under the worker identity | A tool allow/deny rule and OS enforcement have different scopes. Neither defines correct business behavior. |
| Claude Code `/goal` | Repeat toward a stated completion condition | Goal text, evaluator verdicts, turn count and independent check output | The documented evaluator reads the conversation; it does not independently run commands or inspect files. It does not change the permission mode. |
| Claude Code `/loop` | Schedule another attempt | Schedule, job identifier and observed invocation time | A trigger says when to run. It supplies neither an acceptance oracle nor release authority. |
| Subagent | Delegate / Observe: separate tasks and context | Prompt, returned artifact, tools and independently checked result | A separate context is not automatically a separate oracle or a security sandbox. |
| MCP | Delegate / Observe: expose structured tools | Server/tool identity, request, response and the governing resource version | Protocol-valid data can still be stale, unauthorized for the proposed action, or semantically wrong. |

## Capture a real adapter observation

Record the installed client and version before interpreting a command. Save the
work order, effective configuration and protected-file identities; invoke the
client in a disposable copy with an explicit budget. Preserve all returned
output, changed files, check commands and exit statuses. Run the acceptance
checks separately, then bind the review decision to that candidate. The five
retained current episodes in this edition use the ChatGPT Work collaboration
interface; they are not executions of the native clients listed here.

The product syntax belongs here, away from the book's stable decision rules.
For example, Claude Code's documented `/goal <condition>` sets a session goal;
`/goal clear` removes it. `/loop <interval> <prompt>` requests recurring work.
These are **documentation examples, NOT_RUN in this edition**. Do not put a
production action into either command until the corresponding work order and
authority are concrete.

## Primary documentation

- [Codex / ChatGPT agent configuration: AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), reached from the official Codex guide.
- [OpenCode: rules](https://opencode.ai/docs/rules/).
- [Claude Code: extension mechanisms](https://code.claude.com/docs/en/features-overview).
- [Claude Code: permissions and sandboxing](https://code.claude.com/docs/en/permissions).
- [Claude Code: goals](https://code.claude.com/docs/en/goal).
- [Claude Code: scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks).
- [MCP: security considerations](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices).

These links and their access date establish the documentation used. They are
not claims that every feature is available in every account, provider or
client version. A future adapter run must record its own capabilities.
