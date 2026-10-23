# Chapter 7 — Plan Work, Delegate Tasks and Coordinate Responsibility

[Home](../README.md#find-your-chapter) · [Lab guide](../navigation/LAB_GUIDE.md) · [Previous: Chapter 6](README_CP06.md) · [Next: Chapter 8](README_CP08.md)

> Checkpoint counts below are historical. Use the [shared lab guide](../navigation/LAB_GUIDE.md#start-with-the-shared-regression-suite) for current checks and candidate-readiness reporting.

**Parent**: CP06 source release, with seven acceptance tests plus 172 general tests = **179 passing offline tests** on extraction.
The parent QA report is correct: the runner prints these two suites separately. CP07 has 179 + 50 = **229 tests**.

From this `companion/` folder:

```bash
python reader_side/tools/run_checks.py
python reader_side/tools/planning_gate.py  # deliberately wrong starter, expected FAIL
python reader_side/tools/planning_gate.py \
  --plan reader_side/reference_solution/delegation_plan.json \
  --handoff reader_side/reference_solution/delegation_handoff.json  # expected PASS
```

The editable starter records are:

- [repo/engineering/planning/delegation_plan.json](../repo/engineering/planning/delegation_plan.json)
- [repo/engineering/planning/delegation_handoff.json](../repo/engineering/planning/delegation_handoff.json)

Only edit those two files in the reader exercise. The *reference* pair is in
[reader_side/reference_solution/](../reader_side/reference_solution) and is protected by the source-manifest model.
It correctly keeps ADR-005 pending human technical review and implementation/release blocked.

## What the checks demonstrate

- Selected task graph, owner dependency, permitted-path, resource-budget and handoff conditions.
- Selected source-fingerprint mismatches and seeded unauthorized-approval errors.
- Logical grouping of independent, read-only investigations (not timings).

## What the checks do NOT demonstrate

- Real agent productivity, live Copilot/Claude/Codex/Kiro execution, actual subagent permission enforcement or process isolation.
- Real payment-policy authority, architecture acceptance, feature readiness, release approval or business value.
- General security against attackers able to rewrite checks or their host runtime.

The runner must be separately authorized and operated for any meaningful anti-tamper claim.
