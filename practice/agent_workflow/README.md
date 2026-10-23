# Work visibly with a coding agent

[Home](../../README.md) · [Practice catalogue](../README.md) · [Chapter routes](../../navigation/CHAPTER_ROUTES.md)

These original practice cards accompany Chapters 1, 2, 6, 7 and 8. They use the
existing Treasury lab and do not change its policies, candidate scopes or oracles.
Run commands from the lab working-copy root unless a card says otherwise.

| Your question | Card | Output |
|---|---|---|
| How much evidence does this change need? | [Proportionate controls](proportionate_controls.md) | One justified control choice, not a universal checklist |
| What did the assistant actually change? | [Observed CP01 repair](observed_cp01.md) | Task, raw commands, patch, red/green checks and limits |
| What belongs in a task, rule or skill? | [Context lifecycle](context_lifecycle.md) | Source selection and a maintenance decision |
| Should I use another agent? | [Pattern selector](pattern_selector.md) | Work-structure decision and a stop condition |
| How do I retain my implementation session? | [Implementation session](implementation_session.md) | A bounded task and evidence-linked review package |

For the separate MCP/CLI comparison, see `../mcp_cli/README.md`. It is a local
integration exercise, not evidence that a named commercial coding client was used.

The retained `runs/CP01_CHATGPT_20261020/` example is an **actual ChatGPT workspace
tool session**. The assistant had already seen the teaching reference. It is not
a blind evaluation, a Codex CLI/Claude Code/Copilot/Cursor trial, or an independent
human review. Read its `TASK.md` and `RUN_RECEIPT.json` before drawing a conclusion.
No full-tree pre-edit scope snapshot was captured in that run; the recorded patch
and protected intent/oracle hashes support narrower claims. No model version,
token use, human effort or bill is guessed.

The practice cards are instructions, not permission controls. A checked source
hash establishes identity of the selected bytes, not correctness or acceptance.
T07-04 remains blocked; CP08 remains a separate local presentation exercise.

## Check what can actually run

From `companion/`, run the bounded local preflight before selecting a named
client route:

```bash
python3 practice/agent_workflow/client_preflight.py --output ../client-preflight.json
```

It records PATH lookup and `--version` output for the five listed coding CLI clients, the VS Code launcher,
and the framework/tool executables. It does not inspect accounts, credential
files, subscriptions or model endpoints. A missing executable is a fact about
this PATH. A found launcher can still fail its version command. The report
records those facts separately; neither a path nor a successful version command
establishes login, supported flags or successful generation. Keep its result with the existing `validation/` observation record
and use that client's current help to confirm invocation and permissions.

The retained `runs/CAPABILITY_PREFLIGHT_20261021/CAPABILITIES.json` found none of
`codex`, `claude`, `copilot`, `opencode` or `gemini` on PATH. Consequently this
revision does not invent a named-client journey. A separate collaboration-agent
episode can use the prepared SDD task and external orchestration bridge in
`../sdd/README.md`; its interface, context exposure and generation evidence must
be reported under their actual names. That episode cannot establish native skill
discovery, host MCP loading or the effective sandbox of an unlaunched client.

## Prepare the next real native observation

[The named-host collection route](../../validation/NATIVE_HOST_COLLECTION.md)
creates a starting-tree snapshot, reuses the command recorder shipped in the
standalone companion, and binds first outputs, failures, configuration and
independent checks into a review packet. It keeps one primary observed route
sufficient and permits an honestly unobserved contrast. Its structural check
does not authenticate a client identity, certify permissions or grant acceptance.
