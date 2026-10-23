# CP03 — Discover the Problem and Validate Value

[Home](../README.md#find-your-chapter) · [Lab guide](../navigation/LAB_GUIDE.md) · [Previous: workspace](../navigation/FIRST_WEEK.md) · [Next: Chapter 4](README_CP04.md)

> Checkpoint counts below are historical. Use the [shared lab guide](../navigation/LAB_GUIDE.md#start-with-the-shared-regression-suite) for current checks and candidate-readiness reporting.

**Purpose:** challenge a sponsor's proposed implementation before any code is changed. All business people, records and measurements in this chapter are synthetic educational fixtures. They are not Euronext data, real interviews or a validated business pilot.

## Steps (stdlib Python only)

From the `companion/` directory:

```bash
python reader_side/tools/run_checks.py
python reader_side/tools/discovery_gate.py --candidate repo/engineering/discovery/assessment.json
python reader_side/tools/discovery_gate.py --candidate reader_side/reference_solution/assessment.json
```

The first command runs the cumulative CP01, CP02 and CP03 offline tests. The intentionally wrong starter assessment fails the second command. The third checks the reference scenario and passes. Edit only [repo/engineering/discovery/assessment.json](../repo/engineering/discovery/assessment.json) for this exercise and compare its changes with the source packet and reference. If you want to use an actual coding agent, consult `adapters/` and check installed versions; no such execution is claimed here.

## Expected synthetic observation

12 case records, 10 with both endpoints, 2 excluded, 4 strictly over 24 hours of the 10 measurable cases, median measurable elapsed time 15.5 h. This does not establish what caused the delays, let alone a quantifiable product gain.

The initial proposal (auto-approve below EUR 5,000) contradicts `SRC-POL-001`: the service routes recommendations; it never authorizes payments. The defensible result in this *simulated* scenario is a **conditional go to a limited explanation-only alpha**, subject to real user/operations validation and a named policy owner. No deployment or policy revision is authorized.

## Boundary

`reader_side/` and `repo/` coexist in a downloadable archive. They are **not** separated by an OS sandbox. Hashes and an offline gate detect selected changes when executed from a separately controlled environment; do not treat them as prevention against an agent running with broad permissions. The assessment schema gate detects certain malformed/unsafe answers; a confident but substantively false answer might still pass other, less complete checks.
