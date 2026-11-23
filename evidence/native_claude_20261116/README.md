# Native Claude Code run, 16 November 2026

This folder is the complete `work/` tree of the run described in
[NATIVE_RUN_20261116.md](../../companion/agent_sessions/NATIVE_RUN_20261116.md),
copied after the last decision. Paths inside keep the `work/...` layout the
printed commands use, so the collector and the ledger read it directly.

| Path | Contents |
|:--|:--|
| `work/<mission>/` | The candidate each mission produced, as checked |
| `work/<session>/` | `SESSION.json`, `task.txt`, `runs/NN/` (native events, stderr, final message, before/after snapshots, `INVOCATION.json`, `RESULT.json`) and `decisions/` |
| `work/evidence/` | Every printed check, review and continuation receipt, the operator's probes in `operator/`, `NATIVE_RUN_LEDGER.json` and `NATIVE_COVERAGE.json` |
| `work/notes/` | The operator's decision notes, follow-up task text and the G4 carry-over hashes |
| `work/g3-integration/` | Integration manifest, both combine receipts, operator command records, the extracted package, and the commit history as `integration-history.bundle` and `integration-history.log` |
| `work/g4-ops-v2/`, `work/g4-agent-ask-01/`, `work/g4-agent-usage-limit-01/` | Retained G4 candidate and sessions from before OPS-G4/v3 and from the usage-limit stop |
| `work/client-inspection-claude/` | Local version and flag inspection of the client |

`.git` directories were left out, as in `evidence/agent_process_v4/`. Inspect the
integration commits with `git clone work/g3-integration/integration-history.bundle`.
Absolute paths inside the records point to the operator's original workspace.

```bash
python3 -B companion/agent_sessions/native_ledger.py \
  --workspace-root evidence/native_claude_20261116 \
  --output work/native-ledger.json
```

The operator of every session was an AI. Nothing here shows a human operating,
accepting or learning from a mission.
