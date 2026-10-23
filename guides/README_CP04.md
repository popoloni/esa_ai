# CP04 — Specify Behavior with Contemporary SDD Tools

[Home](../README.md#find-your-chapter) · [Lab guide](../navigation/LAB_GUIDE.md) · [Previous: Chapter 3](README_CP03.md) · [Next: Chapter 5](README_CP05.md)

> Checkpoint counts below are historical. Use the [shared lab guide](../navigation/LAB_GUIDE.md#start-with-the-shared-regression-suite) for current checks and candidate-readiness reporting.

**All people, policies, case data, requests and thresholds are fictional educational material.** The synthetic system makes routing recommendations; it never authorizes or moves funds. Tool descriptions are based on official documentation checked on **19 October 2026**; no live vendor agent was executed.

## Recommended sequence — from this `companion/` directory

```bash
# Cumulative baseline: CP01 + CP02 + CP03 + CP04
python reader_side/tools/run_checks.py

# Deliberately unsafe starter: expected REVIEW REQUIRED, exit 1
python reader_side/tools/spec_gate.py --candidate repo/engineering/specifications/explanation_alpha/specification.json

# Reviewer reference: expected local PASS, exit 0
python reader_side/tools/spec_gate.py --candidate reader_side/reference_solution/specification.json
```

The CI-style runner reports **93 passed** (7 Chapter 1 acceptance, 14 Chapter 2, 25 Chapter 3, 47 Chapter 4). The intentionally unsafe starter returns **11 review findings**. Its correct repair makes the gate pass; the entire cumulative test suite remains green after replacing the editable starter in an isolated copy.

## Lab objective and edit path

- The correct Chapter 3 handoff is held in [reader_side/specs/discovery_handoff.json](../reader_side/specs/discovery_handoff.json), because the older Chapter 3 starter intentionally remains unsafe in the cumulative source snapshot.
- The only Chapter 4 learner-editable artifact is **[repo/engineering/specifications/explanation_alpha/specification.json](../repo/engineering/specifications/explanation_alpha/specification.json)**.
- The reader-owned reference and oracle are under [reader_side/reference_solution/specification.json](../reader_side/reference_solution/specification.json) and [reader_side/specs/case_oracle.json](../reader_side/specs/case_oracle.json).
- The synthetic record says \"explain the existing route\"; it does **not** permit automatic payment approval, a threshold revision, historical changes, or production deployment.
- The five source records in [reader_side/discovery/sources/](../reader_side/discovery/sources) retain their original synthetic authority labels; the stale wiki is never authoritative.

## Optional reviewed projection

```bash
python reader_side/tools/spec_gate.py \
  --candidate reader_side/reference_solution/specification.json \
  --export-reviewed exports/ch04_reference
```

This author-built exporter writes only under `companion/exports/<name>/`. It creates four illustrative projections: portable Markdown, OpenSpec-shaped delta Markdown, EARS-shaped Kiro requirements, and Gherkin-shaped scenarios. **These files were not validated by Spec Kit, OpenSpec, Kiro or a Gherkin runner.** They are examples of format/identity transfer, not verified framework interoperability or human approval.

## Current-tool adapters and the book

Read [adapters/SPECKIT_SPECIFY_2026.md](../adapters/SPECKIT_SPECIFY_2026.md), `OPENSPEC_DELTA_2026.md`, `KIRO_REQUIREMENTS_2026.md`, and `BMAD_BOUNDARY_2026.md`. Each names official current documentation and its unverified integration boundary. Pin actual versions and preserve session logs before claiming any live trial.

## Security and evidence boundary

The protected SHA-256 manifests and structural validator detect a selected subset of bad edits **only if run from a separately controlled trusted process**. The ZIP itself is not an operating-system sandbox. The checker partly uses lexical cues and exact teaching oracle values; it cannot establish independent semantic truth. Business value and operator comprehension have not been validated with people. The correct spec status is **READY_FOR_HUMAN_REQUIREMENTS_REVIEW**, not implementation or release approval.
