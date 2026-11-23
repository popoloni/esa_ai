# Native Claude Code run, 22 November 2026

This folder is the complete `work/` tree of the run described in
[NATIVE_RUN_20261122.md](../../companion/agent_sessions/NATIVE_RUN_20261122.md),
copied after the last decision. Paths inside keep the `work/...` layout the
printed commands use, so the collector and the ledger read it directly.

| Path | Contents |
|:--|:--|
| `work/<mission>/` | The candidate each mission produced, as checked |
| `work/<session>/` | `SESSION.json`, `task.txt`, `runs/NN/` (native events, stderr, final message, before/after snapshots, `INVOCATION.json`, `RESULT.json`) and `decisions/` |
| `work/evidence/` | Every check and continuation receipt, including the superseded `g2-first.json` and `g4-first.json`, and `NATIVE_RUN_LEDGER-02.json` |
| `work/g3-integration/` | Integration manifest and receipt, operator command records, the extracted package, and the commit history as `integration-history.bundle` and `integration-history.log` |
| `work/g4-before-owner-mapping/`, `work/g4-agent-before-owner-mapping/` | The first G4 candidate and session, before the owner mapping; `SESSION.json` still names their original `work/g4` paths |
| `work/g4-standalone/`, `work/g4s-agent/` | A standalone `new G4` session outside the matrix |
| `work/notes/` | The operator's first decision note |

`work/evidence/g2-first2.json` is a passing G2 check written under an ad hoc
name before numbered retries existed; the ledger does not read it.
`g2-first-02.json` repeats that check on the same bytes. `.git` directories were
left out; inspect the integration commits with
`git clone work/g3-integration/integration-history.bundle`. Absolute paths inside
the records point to the operator's original workspace.

```bash
python3 -B companion/agent_sessions/native_ledger.py \
  --workspace-root evidence/native_claude_20261122 --client claude \
  --output work/native-ledger-20261122.json
```

The operator of every session was an AI. Nothing here shows a human operating,
accepting or learning from a mission.
