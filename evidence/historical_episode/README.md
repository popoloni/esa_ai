# Historical episode used in Chapter 1

These records were copied from the supplied d16.4 archive. They describe
historical model executions; no new model execution is implied by their
inclusion in the prototype. `PROVENANCE.json` identifies every copied
source, destination, size and SHA-256. The copies preserve the original
bytes, including historical absolute paths and filenames.

## The directly inspectable episode: 22 October 2026

The source was `practice/native_client/observed/ch01_01` in the companion
at commit `13a1182fc64c2a2c3b3677852b9dfdd95d4be908`. The selected extract
is at `native_20261022/`.

| Read to answer | Included record |
| --- | --- |
| What was requested? | `configuration/TASK_PROMPT.txt` |
| What did the client receive? | `starting_files/` and original task prompt |
| What did the first attempt do? | `attempt_01/native-session.json`, `attempt_01/stdout.txt`, top-level `OUTCOME.json` |
| What assistance changed? | `RECOVERY_INTERVENTION_02.json` and `configuration/TASK_PROMPT_RECOVERY_02.txt` |
| What did recovery do? | `attempt_02/native-session.json`, `stdout.txt`, `OUTCOME.json` |
| What changed in the code? | `independent_review/routing.diff` and `routing.py` |
| Who checked the result? | `independent_review/REVIEW.json` |
| What were the actual checks? | `independent_review/initial_acceptance.json`, `independent_acceptance.json`, `additional_cases.json`, `scope_guard.stdout.txt` |
| What was known in advance? | `INDEPENDENT_REVIEW_PLAN.json` |
| What do the identities and totals cover? | `CLIENT_IDENTITIES.json`, `USAGE.json`, `OUTCOME.json` |

The second native attempt edited the function but timed out before its
planned checker and final summary. The original seven cases and the
fourteen additional predeclared cases passed in the independent
assistant review outside that native session. Those two sets overlap.
The author had prior solution exposure and the recovery supplied
specific API guidance. Human acceptance remained pending. These facts
exclude autonomous, blind-benchmark and complete-productivity claims.

This is a compact selected evidence packet, not the complete repository,
runtime, model weights, client state or a self-contained historical
replay. Large command receipts that embed a complete starting-tree manifest are
omitted; their original hashes and omission reasons are recorded in the
provenance index. Some references inside unchanged raw records identify files in
the larger original packet. Use the source archive when that wider
material is needed. Use the current prototype companion for the new
offline exercises; do not execute the historical absolute paths.

## The later report: 24 October 2026

`D16_DUAL_ROUTE_METAL_REPORT.md` preserves the source report unchanged.
It reports a later M2 Max Metal environment, a guided Brownfield
completion and a Greenfield completion requiring facilitator code
correction. The supplied baseline contains that narrative report; this
extract does not claim to hold the later run's full prompts or raw
sessions. Chapter 1 uses it only for the stated intervention distinction.

## Source and copying boundary

Source archive:
`ESA_d16_4_Final_Current_and_Packt_EN_IT_20261101.zip`.

Library identity: `libfile_42d04849947881919c3fbdc091e699bd`.

Every copied file is listed in `PROVENANCE.json`. New explanatory text
and the index are prototype editorial work; original event records,
candidate sources, prompts and reports are historical observations.
