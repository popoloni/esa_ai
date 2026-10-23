# What this attempt tells us about workflow cost

`WORKFLOW_COST_ACCOUNT.json` accounts for the observations retained by the actual CSV implementation attempt and a separate SDD controller run. Its status is `PARTIAL_ACCOUNT_MISSING_COST_AND_HUMAN_ACCEPTANCE`: the records provide useful elapsed intervals and outcomes, but do not measure a complete workflow cost.

## Read the measurements with their boundaries

| Observation | Retained value | Meaning |
| --- | --- | --- |
| CSV attempt creation to worker finish | 271.344986 seconds | Elapsed interval covering dispatch, implementation and some evidence preparation; the first worker timestamp was not separately captured |
| CSV task-bearing journal actions | 14 | Ten command calls and four patch calls; one patch changes the implementation |
| Worker-authored focused checks | 6 passed | Checks written by the implementer |
| Later selected independent checks | 7 categories passed | Separate automated checks of the selected local contract; duration unmeasured |
| Separate SDD generation stage | 432.951277 seconds | Controller-reported external-worker interval, including dispatch and waiting for submission |
| Separate SDD review stage | 230.068571 seconds | Controller-reported external-worker interval, including dispatch and waiting for submission |

The CSV budget of 360 seconds is a constraint, not measured effort. Journal actions 9–11 overlap; their intervals must not be summed. Tool-reported wall times and tool-output token estimates do not measure active model work or provider usage. The SDD run overlaps the CSV attempt and performs a different task, so adding the two runs or ranking their productivity would be misleading.

The initial CSV failure records the supplied unimplemented feature before the implementation patch. It is retained as part of the work, but does not count as a failed model-generated candidate. The SDD generator also recorded a refused helper spawn: the thread limit prevented that helper from running. Neither event has separately attributable effort or monetary cost.

## What remains unknown

Preparation before the attempt, active model work, human review, later independent-check duration, rework effort, maintenance, provider token usage and attributable bills are all `null` with reasons in the account. No cost assumptions have been inserted. Missing values do not mean zero.

One CSV candidate passed selected automated checks. The SDD controller stopped at `WAITING_HUMAN`. Neither record supplies an accountable human acceptance, so the human-accepted-outcome denominator is also `null`. Total workflow cost, cost per accepted outcome and ROI cannot be calculated from these records.

For a future complete account, time preparation and review from the beginning, retain unsuccessful candidates and rework, record attributable usage and bills, and preserve the human decision for the exact delivered candidate. Keep measured values separate from rate or allocation assumptions. Extend the account only with new observations; do not infer missing historical measurements from elapsed time.

## A visible provenance correction

The original `START.json` task digest matches `TASK.txt` with its final newline removed, not the exact stored bytes. `TASK_IDENTITY_CORRECTION.json` records both digests and shows that the first task read retained in journal entry 2 equals the current task bytes exactly. No substantive task-content discrepancy was found. The original start record and task remain unchanged; the correction does not alter the session's timing or acceptance status.

The JSON account includes paths and SHA-256 hashes for the session, journal, source identities, independent checks, SDD state and provenance records. These allow a reader to distinguish a measured interval, a declared budget, a missing cost and a recorded decision.
