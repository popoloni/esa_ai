# Native run of all eight missions, 16 November 2026

All eight missions and all twelve required stages of `NATIVE_SESSION_MATRIX.json`
completed through `agent_session.py` with a native coding client, and every
mission's printed protected check and continuation passed on the candidate the
agent produced. `native_ledger.py` reports `verified_native_missions: 8`.

The operator was an AI. Claude (model `claude-opus-5-5`), working in the author's
review session, wrote the operator questions, launched each run, read the events,
ran the protected checks and its own probes, and recorded every decision with
`--operator-kind AI`. No human operated, steered or accepted a mission. This run
closes the *native-route* gap; it does not close the *human-operator* gap.

## Setup

| Item | Value |
|:--|:--|
| Client | Claude Code 2.1.325, `--client claude` (new in edition 5.1) |
| Worker model | `claude-sonnet-5-5`, requested and observed in every `init` event and assistant `message.model` |
| Launch profile | Six built-in tools; Bash limited to listed prefixes; no MCP servers, skills, browser, user settings or session persistence; `--max-budget-usd 5` per launch |
| Operator | AI (Claude, `claude-opus-5-5`); every decision file says so |
| Window | 22:11–22:28 UTC (23:11–23:28 Europe/Rome) |
| Reported client cost | 2.01 USD for the twelve matrix stages; 2.18 USD for all fifteen launches |
| Codex CLI | Not installed in this environment; that route remains unverified |

## Stages

| Stage | Launches | Time | Cost (USD) | Denied operations | Operator decision | Final gate |
|:--|:--|--:|--:|--:|:--|:--|
| G1 question | 1 | 25 s | 0.067 | 0 | stop (asked the right question) | owner response released |
| G1 implementation | 1 | 45 s | 0.160 | 2 | accept | slice 4/4; handoff ready |
| G2 | 1 | 99 s | 0.287 | 4 | accept | 17/17; handoff ready |
| G3 | 2 | 85 + 57 s | 0.437 | 6 | correct, then accept | 7/7; handoff ready |
| G3 report role | 1 | 23 s | 0.081 | 1 | accept | integration 9/9 on the extracted package |
| G3 CLI role | 1 | 23 s | 0.072 | 0 | accept | integration 9/9 on the extracted package |
| G4 | 1 | 48 s | 0.153 | 1 | accept | 11/11; handoff ready |
| B1 v1 | 1 | 34 s | 0.116 | 2 | accept | 12/12; context handoff ready |
| B1 v2 | 1 | 39 s | 0.123 | 2 | accept | 18/18; context handoff ready |
| B2 | 1 | 45 s | 0.133 | 2 | accept | 12/12; handoff ready |
| B3 | 1 | 56 s | 0.191 | 3 | accept | 10/10; handoff ready |
| B4 | 1 | 53 s | 0.192 | 1 | accept | 7/7; handoff ready |

Two further G4 sessions are retained outside the matrix: one stopped by an
account usage limit before any model work (`CLIENT_EXIT_NONZERO`, cost 0), and
one in which the worker stopped and asked (below).

## What the operator had to decide

**G1, question stage.** The worker stopped without implementing and asked what
`get_reservation` returns for an absent identifier, the same gap the operator had
written down. Only then was the supplied owner response released.

**G2, the worker refused its own predecessor.** The native G1 stores
`g1_reservation(id, …)`, which no G2 decision authorizes. The worker migrated the
three authorized representations and refused its own lineage's table with "owner
mapping required", leaving the bytes unchanged. That is the contracted behaviour.
The checks do not exercise it, because the continuation migrates the reference
representation; the operator probed it separately.

**G3, an operator error.** The first G3 run blocked: every protected method
failed in `setUp` because the test fixture builds the reference G2 layout, which
the candidate refused. Part V says the AP-G3 task required *both* the retained G2
schema and the supplied fixture; the operator's task had omitted that. A bounded
follow-up with the printed AP-G3 wording passed. The failed receipts are retained.

**G3 integration, a checker defect.** Both role checks passed, but the first
combination blocked: `verify_transport.py` required `cancel()` to equal the
reference dictionary `{status, code, version}` exactly, and the native candidate
also returns `reservation_id`. Neither RES-002/v1 nor INTEGRATION-G3/v1 fixes the
key set, and the protected G3 tests read only those three fields. The checker was
narrowed to the contracted fields; the resumed combination passed nine of nine
cases on the extracted package. The blocked receipt is retained.

**G4, ASK and a contract extension.** OPS-G4/v2 recognised only the reference and
the AP-recorded schema-3 tables and said it "does not certify an arbitrary schema3
database". The worker implemented `diagnose` and `cost_summary`, then stopped
because the native G3 table matches neither (8 of 11 methods). Following the
precedent of G2-OD-02 and OPS-G4/v2, both authored by the AI recording operator
under the author's instruction, the operator authored **OPS-G4/v3**, adding the
native signature. G4 was re-advanced from the same accepted G3 integration with
the worker's two files carried over unchanged (hashes in
`work/notes/g4-carry-02.txt`), and a fresh session passed.

## Instruction versus enforcement

The client denied 25 operations across the fifteen launches, all reported in the
final `permission_denials` field: compound commands, environment-variable
prefixes, heredoc writes, and one `Write` to the package root outside the
candidate. Each time the worker found an allowed route and said so. Three
observations matter for Chapter 4:

- Claude Code gives each session a scratchpad directory outside the candidate and
  permits writes there. Several workers wrote probe scripts in it, contrary to the
  literal task wording. The candidate snapshot does not cover that directory.
- In `acceptEdits` mode the client also approved `rm -rf __pycache__` inside the
  CLI worktree without a denial.
- Workers ran read-only `git status` in parent directories and reported the
  operator's own uncommitted adapter edits in this package.

## Open owner questions

1. G2: may records written by the native G1 representation `g1_reservation` be
   mapped column for column, like G2-OD-02? Nothing was invented; migration
   refuses them.
2. B3: does "retains the legacy table unchanged" cover only rows, or also the
   triggers the supplied migration adds?
3. OPS-G4/v3 is an AI-authored teaching-case extension and needs the author's
   review. It still cannot certify any other learner schema; a general mapping
   step would remove the problem for every lineage.

## Changes in companion 5.1

| File | Change |
|:--|:--|
| `companion/agent_session.py` | `--client claude`, Claude stream-json observations, spend ceiling, isolation profile |
| `companion/agent_sessions/collect_native.py` | Accepts both runtime labels; records client, cost and denials |
| `companion/agent_sessions/verify_native_capture.py` | 28 new synthetic Claude controls (87 in all) |
| `companion/agent_sessions/native_ledger.py` | New: joins captures, decisions and receipts per mission |
| `companion/integration_assets/verify_transport.py` | Checks the contracted cancellation fields, not the reference dictionary |
| `companion/contracts/G4.md`, `checks/fixtures/g4_fixture.py`, `solutions/G4/operations.py` | OPS-G4/v3 with the native signature |
| Work orders, curriculum manifest, `missions/G4.*` | Label OPS-G4/v3 |
| `evidence/native_claude_20261116/` | The complete run: sessions, candidates, receipts, operator notes and probes |

A defect that predates 5.1 is unchanged: the replay command printed in
`companion/integration_assets/README.md` needs
`evidence/agent_process_v4/AP-INTEGRATION/packages/integration-001.zip`, which
the public companion does not include. The guide now says so.

## What this run does not establish

- Human operation, human acceptance, usability or learning: no person took part.
- The Codex CLI route: it was not available here.
- Stability: each stage ran once with one model; a different run can differ.
- Owner authority: every owner decision remains part of the fictional case.

## Check it yourself

```bash
python3 -B companion/agent_sessions/collect_native.py \
  --workspace-root evidence/native_claude_20261116 \
  --output work/native-coverage.json
python3 -B companion/agent_sessions/native_ledger.py \
  --workspace-root evidence/native_claude_20261116 \
  --output work/native-ledger.json
```

Both read retained files only and launch nothing.
