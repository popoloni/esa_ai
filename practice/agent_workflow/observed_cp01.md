# An observed repair by this edition's ChatGPT assistant

The files in `runs/CP01_CHATGPT_20261020/` record an actual local sequence on
20 October 2026. They identify the actor as the **current ChatGPT assistant using
workspace tools**. No installed commercial coding-agent CLI was used. The
assistant had already inspected the teaching reference during editorial work;
this is a worked repair, not an unseen task or a comparative performance trial.

## Follow the evidence

| Step | Retained evidence | What you can conclude |
|---|---|---|
| Prepare | `CMD01_PREPARE.stdout.log` | The helper created a disposable full lab; only its router was replaced with the known faulty starter; source companion and reader-side bytes were unchanged during preparation |
| Observe | `RED_RESULT.json`, raw command logs | Python 3.12.14 ran seven cases: three passed, two failed and two errored |
| Diagnose | `AGENT_PATCH.tool.txt`, baseline source | Negative/zero input reached a normal route; malformed input and NaN caused exceptions |
| Edit | `candidate.patch`, `candidate_routing.py` | The assistant added parse-exception handling and explicit finite/positive checks; existing threshold branches stayed intact |
| Recheck | `GREEN_RESULT.json`, raw command logs | The same seven cases passed; recorded intent and acceptance hashes were unchanged; selected protected integrity checks had no findings |
| Decide | `RUN_RECEIPT.json` | Human review is still pending; no release, payment, product comparison or productivity claim follows |

The proposal became an action only when the workspace patch tool ran. The green
result exists because Python executed the separately supplied cases, not because
the assistant wrote that the code was correct. The full exception traces and
expected nonzero red exit are retained rather than replaced by the successful
summary.

The exact tool patch and command records show the observed work. No full-tree
pre-edit snapshot was captured, so this record does not independently establish
whole-workspace edit scope or OS confinement. The source-level candidate diff and
intent/oracle identity are narrower, inspectable evidence. Chapter 8 shows a
before-edit baseline when a gate will claim actual edit scope.

`elapsed_ns` records subprocess intervals, not total authoring time, human review
effort or a benchmark. Model version, billing and tokens were not independently
captured and remain null. A new reader's run should record its own environment
and actual result rather than copying this receipt.
