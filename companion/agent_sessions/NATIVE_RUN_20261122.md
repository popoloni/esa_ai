# Second native run of all eight missions, 22 November 2026

A second Claude Code run took all eight missions and all twelve required stages
of `NATIVE_SESSION_MATRIX.json` through `agent_session.py`, from a fresh
extraction of the public companion. It found one companion defect on the
Reservation route. The defect was fixed and G4 was run again on the same
lineage. `native_ledger.py` then reports `verified_native_missions: 8` with all
twelve capture stages.

The operator was an AI (Claude, working in the author's session) and recorded
every decision with `--operator-kind AI`. No human operated, steered or accepted
a mission.

## Setup

| Item | Value |
|:--|:--|
| Client | Claude Code 2.1.330, `--client claude`, logged in |
| Worker model | `claude-sonnet-5-5`, requested and observed, in eleven matrix stages; the G1 question stage ran without `--model` and observed the client default, `claude-opus-5-5` |
| Launch profile | As in the 16 November run; `--max-budget-usd 5` per launch |
| Reported client cost | 2.02 USD for the twelve matrix stages; 2.43 USD for all fourteen launches |
| Evidence | `evidence/native_claude_20261122/` |

## Stages

| Stage | Time | Cost (USD) | Denied operations | Decision | Protected check |
|:--|--:|--:|--:|:--|:--|
| G1 question | 52 s | 0.255 | 1 | stop (asked the right question) | owner response released |
| G1 implementation | 50 s | 0.225 | 4 | accept | slice 4/4; handoff 6/6 |
| G2 | 92 s | 0.299 | 2 | accept | 17/17; handoff ready |
| G3 | 56 s | 0.192 | 0 | accept | 7/7; handoff ready |
| G3 report role | 27 s | 0.106 | 4 | accept | integration passed on the extracted package |
| G3 CLI role | 18 s | 0.071 | 0 | accept | integration passed on the extracted package |
| G4, first attempt | 63 s | 0.211 | 2 | ask | 9/13 (retained outside the matrix) |
| G4, after the fix | 50 s | 0.185 | 1 | accept | 13/13; handoff ready |
| B1 v1 | 27 s | 0.115 | 4 | accept | 12/12; context handoff ready |
| B1 v2 | 31 s | 0.117 | 2 | accept | 18/18; context handoff ready |
| B2 | 41 s | 0.131 | 1 | accept | 12/12; handoff ready |
| B3 | 33 s | 0.146 | 1 | accept | 10/10; handoff ready |
| B4 | 47 s | 0.177 | 1 | accept | 7/7; handoff ready |

A standalone `new G4` session (65 s, 0.201 USD, 13/13) is retained as
`work/g4s-agent` and is not a matrix stage. Every worker stayed inside its
allowed files.

## What the run found and what changed

**G3 to G4: a lineage layout that no contract named.** This lineage's G3 kept
its reservations in a table named `reservations_v3`, with the native column
list. OPS-G4/v3 names `reservations` and two `reservations_v2` layouts, so the
first G4 worker implemented those three, refused this one and asked for an owner
mapping, which is the contracted behaviour. The protected check could not pass:
four methods failed because the corruption fixture builds only named layouts.
The 16 November run met the same class of problem and answered it by writing
OPS-G4/v3 for its own table. A reader whose agent picks any other name had no
documented way forward.

The companion now handles this at `advance G4`. When the retained G3 creates a
layout that OPS-G4/v3 does not name, `advance` writes the owner decision
G4-OD-01 for that lineage alone (`docs/G4-OD-01.md` and `docs/G4-SCHEMA-MAP.json`),
provided every column uses a name the named layouts already give to the same
role. Otherwise it refuses and explains how to supply a mapping with
`--schema-map`, which it checks against the columns `init_db` creates. The
contract, the tests and their count are unchanged; the fixture and the
reference observer read the mapping when it exists. G4 was re-advanced from the
same accepted G3 integration. The second worker read the decision, implemented
the mapping generically, probed a wrong signature and a competing pair itself,
and passed 13/13 and the handoff. The first attempt is retained as
`work/g4-before-owner-mapping` and `work/g4-agent-before-owner-mapping`.

**Receipts: a used name could not be superseded.** The operator ran the printed
G2 check once before the agent, which consumed `g2-first.json`; the ledger then
read that failing receipt, although the agent's candidate passed 17/17. The
ledger now reads numbered retries of every printed receipt (`g2-first-02.json`,
...) and gates on the most recently recorded one, listing earlier ones as
superseded. The CLI's refusal names the next free retry. G2 and G4 gate on
their `-02` receipts.

`verify_curriculum.py` adds a deterministic control: a G3 lineage built from the
reference by renaming its table goes through integration and `advance G4`;
an observer that ignores the mapping fails four methods; the reference passes
the handoff; three malformed or unnecessary operator maps are refused.

## Limits

One run per stage shows that the lineage gap occurs, not how often. Codex CLI
was not available here. No human operator, reader trial or human acceptance is
represented.
