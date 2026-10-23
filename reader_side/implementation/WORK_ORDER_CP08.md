# CP08 local teaching work order — integrated companion

**Purpose:** build and debug a bounded explanation adapter using the shared
CP01–CP07 teaching materials and the synthetic proposal `SPEC-004/v1`.

The canonical Chapter 7 plan `PLAN-007/v1` and handoff `HOF-007/v1` are present.
They record `PLANNING_ONLY_NOT_EXECUTED`: T07-04 is blocked pending a human
architecture decision, and release is not authorized. This work order permits a
local classroom exercise in a disposable copy. It does not mark T07-04 executed,
replace its proposed write path, accept ADR-005, or grant release authority.

## Candidate boundary

Exactly two paths, relative to `repo/`, may change in this exercise:

- `src/treasury/explanation_alpha.py`
- `engineering/implementation/implementation_report.json`

The adapter displays a result from the existing routing/design code. Preserve
BR-001/v1 and the EUR 5,000 boundary. A routing recommendation must never become
payment authorization, and an unmeasured benefit must remain a hypothesis.

The router, specification, acceptance cases, source catalogue, context/skill,
planning artifacts, ADR-005, independent checks and production configuration are
outside this exercise's edit scope. No credentials, network services, deployment
or payment movement are part of the task.

## Reader-owned evidence

From `companion/`, capture the repository state **before candidate edits**:

```bash
python reader_side/tools/scope_guard.py --chapter CP08 --capture reader_side/evidence/CP08_EDIT_BASELINE.json
```

Keep that baseline unchanged and supply it to each candidate gate invocation:

```bash
python reader_side/tools/implementation_gate.py --scope-baseline reader_side/evidence/CP08_EDIT_BASELINE.json
```

Only a supplied, retained before-edit baseline supports the actual edit-diff
scope check. Global protected-file integrity runs regardless. Chapter-specific
path checking rejects the router even though earlier exercises historically
permit editing it. All checks are pedagogical reader-side controls, not an OS
sandbox or a substitute for reviewing the diff.

## Done for this lab

Selected owner-side cases and report checks pass; the actual diff respects the
two-path boundary; the shared harness passes; and a review note identifies
remaining human architecture, usability/value and release decisions. Stop at
`READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED`. A green harness or a reference-solution run
does not by itself establish that the learner candidate passed.
