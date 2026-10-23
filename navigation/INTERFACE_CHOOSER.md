# Choose an interface for one actual job

Start from the operation and its target. A terminal command, an MCP tool and a
remote API can all retrieve a policy record; their operational boundaries differ.
The choices below are engineering guidance, not a performance ranking.

| Job | A proportionate starting point | Where data and authority cross | Evidence to retain |
|---|---|---|---|
| A known local operation with explicit arguments, such as a fixed policy lookup or test command | The existing CLI, when it already exposes the required operation | The invoking process selects its command, working directory, files and environment. Process rights and any configured credentials remain separate from the requested task. | Literal executable and arguments, version, selected inputs, exit status, stdout/stderr and changed files. |
| A model must discover and select among a small set of described operations | An MCP server with narrowly described tools | The host connects a client to the server, loads tool information according to its own behavior and dispatches selected calls. Local stdio connects processes; the server's OS rights require their own control. | Effective host configuration, actual discovery, model-selected tool event, request/response and server diagnostics. |
| A task needs restricted data in another service | Its supported authenticated remote interface; use remote MCP when its tool integration helps the host | Requests leave the local process. Inspect the service endpoint, resource owner, client/service authorization and requested scope, plus which returned data the host sends to a model. | Authorized target/account identity, scope and consent record where applicable, request/result IDs, service-side observations where available. Keep credential values out of evidence. |
| Any interface can create or change external state | Add a bounded write contract to the selected interface | Name the exact target, allowed mutation, actor and decision owner. Authentication establishes a caller relationship; it does not settle whether this task may make this change. | Before/after state, actual result, retry identity, owner decision and recovery or reconciliation procedure. If the result is uncertain, inspect before retrying. |

## Apply the choices to this companion

For one known `BR-001/v1` lookup, use
`python3 practice/mcp_cli/policy_cli.py lookup BR-001/v1`. If the lesson is tool
discovery and model selection, use the separately observed local MCP route.
Both are documented in the [comparison](../practice/mcp_cli/README.md) and
[native guide](../practice/native_client/README.md). The returned policy's meaning
is unchanged by the interface.

The remote and write rows are **documentation-based planning examples, not
executed remote integrations in this edition**. For a ticket-update example,
identify the allowed ticket and fields, inspect the current value, record the
actual write response and reconcile an uncertain retry. Do not assume an undo
exists or that repeating a request is harmless. Chapters 10–12 supply the
artifact, identity and recovery reasoning; they do not prove a remote service's
particular semantics.

MCP separates protocol exchange from how a host manages model context. Its
current architecture describes local stdio and remote Streamable HTTP routes
[1]. The current authorization specification describes HTTP authorization;
it treats stdio credentials separately [2]. A localhost endpoint or read-only
tool description does not impose a process sandbox. The official security
guidance treats server launch, permissions and containment as explicit controls
[3]. Check those actual boundaries in the chosen host.

Tool descriptions do not have one universal context cost. Some hosts load them
early; others can discover and load selected definitions later. Anthropic's
documented deferred-loading example illustrates one such mechanism [4]. Inspect
the actual host, version, configuration and returned metadata before claiming
that every schema was loaded or that MCP always consumes more context than a
CLI. Serialized request bytes are not automatically model-token or billing data.

## Primary references

Checked 22 October 2026. These are documentation references; they do not extend
the companion's observed runtime claims.

1. [MCP architecture, 2026-07-28](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture): protocol scope, participants and transports.
2. [MCP authorization, 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization): HTTP scope, roles, resource-owner authorization and stdio distinction.
3. [MCP security guidance, dated 2025-11-25 route](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices): local server launch and OS permissions; proxy and credential boundaries.
4. [Anthropic, advanced tool use](https://www.anthropic.com/research/advanced-tool-use): deferred tool definitions and host/provider-specific loading behavior. Vendor performance figures are not adopted as results for this companion.
