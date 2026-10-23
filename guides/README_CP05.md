# Chapter 5 — Explore Architecture and Prototype Alternatives

[Home](../README.md#find-your-chapter) · [Lab guide](../navigation/LAB_GUIDE.md) · [Previous: Chapter 4](README_CP04.md) · [Next: Chapter 6](README_CP06.md)

> Checkpoint counts below are historical. Use the [shared lab guide](../navigation/LAB_GUIDE.md#start-with-the-shared-regression-suite) for current checks and candidate-readiness reporting.

This CP05 checkpoint extends CP04 without changing earlier checkpoint directories.
It is entirely synthetic and runs offline with Python standard library only.

## Sequence

1. Run `python reader_side/tools/run_checks.py` — cumulative regression suite.
2. Inspect [repo/engineering/architecture/architecture_decision.json](../repo/engineering/architecture/architecture_decision.json) and `ADR-005.md`: deliberately wrong starters.
3. Inspect both prototypes in [repo/src/treasury/architecture/](../repo/src/treasury/architecture) and compare against [reader_side/specs/case_oracle.json](../reader_side/specs/case_oracle.json) (read only).
4. Run `python reader_side/tools/architecture_gate.py` (expected FAIL for starter).
5. Correct only the candidate files. See [reader_side/reference_solution/](../reader_side/reference_solution) for the reference *after* attempting.
6. Run `python reader_side/tools/architecture_gate.py --candidate reader_side/reference_solution/architecture_decision.json --adr reader_side/reference_solution/ADR-005.md` (expected PASS).
7. Re-run cumulative [run_checks.py](../reader_side/tools/run_checks.py); do not modify reader-side test/oracle/guard scripts.

The reference choice of direct is a context-dependent teaching recommendation,
not an empirically established superior architecture. Both alternatives pass
8 selected synthetic cases; no latency benchmark, human comprehension study,
OS sandbox or live Kiro/Copilot invocation is claimed.

## Review handoff

A passing local gate means only that the nominated structure and behaviors
satisfy selected checks. A human must review the trade-off and choose the
implementation. The ADR status remains `PROPOSED_FOR_HUMAN_ARCHITECTURE_REVIEW`.
