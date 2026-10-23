# Chapter 9 — Verify Behavior, Security and Quality Independently

[Home](../README.md#find-your-chapter) · [Lab guide](../navigation/LAB_GUIDE.md) · [Previous: Chapter 8](README_CP08.md) · [Next: Chapter 10](README_CP10.md)

> Checkpoint counts below are historical. Use the [shared lab guide](../navigation/LAB_GUIDE.md#start-with-the-shared-regression-suite) for current checks and candidate-readiness reporting.

The active Chapter 9 exercise now lives in the **unified `companion/`** alongside the earlier chapters. The original CP05-derived checkpoint remains unchanged in `snapshots/CP09_companion/` as historical evidence. Its former standalone test count is not the unified suite's count; consult the current integrated validation report.

## Two verification paths

The **CP09 wrapper exercise** retains its deliberately unsafe candidate, editable review record, protected unsafe fixture and protected safe reference. It teaches why self-consistency is insufficient and why the reviewer must reject incorrect behavior or inflated review claims.

The **cross-chapter integration bridge** checks the actual CP08 `build_explanation` implementation against the independent CP09 oracle. It also checks the presentation label and upstream evidence receipts. The wrapper reference calls the earlier architecture presenter directly; passing that reference alone is not evidence that the CP08 implementation passes the bridge. Use the unified integration guide and runner for the bridge verdict.

## Wrapper exercise commands

From the book-package root, change to `companion/`. The tools use only Python's standard library:

```bash
python3 reader_side/tools/run_checks.py

# Intentionally faulty editable starter: expected FAIL.
python3 reader_side/tools/verification_gate.py

# Protected reference: expected PASS_REVIEW_GATE_ONLY.
python3 reader_side/tools/verification_gate.py \
    --candidate reader_side/reference_solution/ch09/safe_candidate.py \
    --review reader_side/reference_solution/ch09/reference_review.json
```

To check the actual edit diff for the Chapter 9 task, supply the owner-created scope baseline using `--scope-baseline PATH`. The baseline must describe the repository before the task's changes. A failure to read or check it is a failed gate. The scope check does not infer authorization from a broad cumulative allowlist.

## Exercise and repair

1. Read [reader_side/specs/case_oracle.json](../reader_side/specs/case_oracle.json) (eight selected owner-controlled cases), [reader_side/reference_solution/specification.json](../reader_side/reference_solution/specification.json) (`SPEC-004/v1`), and [reader_side/discovery/sources/SRC-POL-001.json](../reader_side/discovery/sources/SRC-POL-001.json) (`BR-001/v1`).
2. Inspect [reader_side/verification/circular_smoke.py](../reader_side/verification/circular_smoke.py): its self-consistency test intentionally passes even for the protected faulty fixture.
3. Fix only [repo/engineering/verification/candidate.py](../repo/engineering/verification/candidate.py) and [repo/engineering/verification/review.json](../repo/engineering/verification/review.json) for this wrapper exercise. A routing recommendation is not payment authorization; the policy boundary remains EUR 5,000.
4. Run the gate. The review record must identify the candidate's current SHA-256, selected-case and manually seeded fault counts, unresolved questions, and `release_authorized: false`.
5. Rerun the unified suite. Negative-control tests use the protected unsafe fixture, so they remain valid after a learner repairs the editable candidate.

Invalid candidate syntax, missing imports or callable entry points, unreadable sources, malformed review JSON and invalid review shapes produce structured failure evidence. This improves error reporting; it does not turn the known-fixture loader into an isolation boundary.

## Evidence and authority

The eight oracle cases and three manually seeded output-level faults are selected synthetic checks. They are not a proof of all inputs, a source-code mutation score, a live-model benchmark, a security audit or stakeholder validation. The owner-side oracle and checks must remain outside the learner's edit authority.

The CP07 production-style implementation task and the proposed ADR retain their pending human decisions. The local CP08/CP09 teaching progression does not mark those decisions accepted or authorize payment, merge, deployment or release. `PASS_REVIEW_GATE_ONLY` is a technical teaching verdict, not human acceptance.

Known author-created modules execute locally. Use the supplied fixtures; the narrow source precheck is not a sandbox for arbitrary untrusted code.
