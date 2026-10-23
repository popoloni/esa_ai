# Implementation Plan: Explain Treasury Routing Recommendations

**Branch**: Not created; supplied scaffold identifier 001-explain-treasury. **Date**: 2026-10-21. **Spec**: spec.md.

**Input**: Candidate artifacts/spec.md derived from SPEC-004/v1, DISC-003/v1, supplied policy records, oracle, assessment, and source/treasury/routing.py.

**Status**: Conditional planning proposal only. Human requirements approval PENDING; downstream design, implementation, and release BLOCKED. No native Spec Kit command, commercial model CLI, or application implementation ran.

## Summary

Propose an explanation-only presentation of an existing routing decision. It must preserve route, reason, and the policy version carried by that decision, and display an explicit separate-human-payment notice. No threshold change, approval action, fund movement, or history rewrite is included.

The inspected routing source defines THRESHOLD_EUR as Decimal("5000.00"), POLICY_VERSION as BR-001/v1, a frozen RoutingDecision with route/reason/policy_version, and assess(amount_eur). Its text rejects parsing failures, non-finite values, and amounts at or below zero; finite positive amounts below the threshold receive STANDARD_QUEUE/BELOW_LIMIT; amounts at or above receive HUMAN_REVIEW/AT_OR_ABOVE_LIMIT. This was a static inspection, not a runtime test or production assessment.

The proposed approach is to present an existing decision without duplicating threshold logic or recomputing historical decisions. Interface selection and provenance retrieval remain undecided. The plan records future work; it does not authorize that work.

## Technical Context

| Item | Observed or pending |
| --- | --- |
| Language/version | Supplied routing source is Python, using dataclasses and decimal. Exact supported runtime version is not supplied: NEEDS CLARIFICATION before implementation. |
| Primary dependencies | Existing source uses standard-library dataclasses and decimal. No new framework, UI library, service, or client is selected. |
| Storage | No storage design is authorized. Historical decisions must retain their attached versions; their retrieval mechanism is not supplied. |
| Testing | Eight author-owned oracle cases and exact Given/When/Then examples are available. A test framework is not supplied; later test harness selection is pending. No application tests ran in this attempt. |
| Target platform | NEEDS CLARIFICATION: current operator surface and deployment environment are absent. |
| Project type | Existing Python routing module; explanation surface remains a choice for authorized design. |
| Performance goals | No defensible latency, throughput, or scale targets are supplied. Owners must establish them from actual workflow needs; none are invented. |
| Constraints | Recommendation only; BR-001/v1; exact EUR 5000 boundary; immutable historical policy provenance; human payment authorization separate; no input edits or implementation in this attempt. |
| Scale/scope | Candidate explanation-only limited alpha; actual users, sample size, and rollout scope pending. |

## Constitution Check

**Gate result: BLOCKED / NOT RATIFIED.** The supplied .specify/memory/constitution.md contains placeholder project principles, governance, version, and ratification date. It supplies no ratified project constitution. Placeholder examples must not be converted into an approval claim. A responsible human must provide or ratify applicable governance before the later Spec Kit research/design workflow can pass this gate.

| Gate | Evidence | Current state |
| --- | --- | --- |
| Human requirements approval | SPEC-004/v1 handoff and three unresolved questions | PENDING; blocks design/implementation |
| Ratified constitution | Supplied file is still a template | BLOCKED; no pass claimed |
| Policy authority | SRC-POL-001; BR-001/v1 | Governs synthetic candidate; no change authorized |
| Routing/payment separation | REQ-EXPL-002; SRC-RISK-002 | Required in every candidate display; human validation pending |
| Benefit evidence | DISC-003/v1; REQ-EXPL-005 | HYPOTHESIS_NOT_VALIDATED |
| Engineering acceptance | Independent review has not been supplied to this worker | PENDING_INDEPENDENT_REVIEW |
| Release authorization | No release authorization supplied | BLOCKED |

The task explicitly requests a reviewable candidate plan despite unresolved questions. This file is therefore a conditional proposal, not a claim that the native speckit-plan workflow completed. Its Phase 0/Phase 1 gates are not passed. No research.md, data-model.md, contracts, or quickstart are represented as completed approved design.

## Project Structure

### Documentation produced by this attempt

| Attempt-relative path | Purpose |
| --- | --- |
| artifacts/spec.md | First candidate requirements and exact scenarios |
| artifacts/plan.md | This conditional plan and gates |
| artifacts/tasks.md | Pending, dependency-ordered future work |
| artifacts/checklists/requirements.md | Generation self-review with unresolved items visible |
| PROMPT.md | Exact supplied task prompt, dispatch request, and TASK.md |
| PROVENANCE.json | Actual interface, exposed identity, unknown metrics, and scope |
| TOOL_ACTIONS.json | Tool actions and their purposes/outcomes |
| INPUT_SNAPSHOT.json | Input hashes for change detection, not an OS barrier |
| CHECKS.json | Actual structural/content checks; not human acceptance |
| RAW_RESPONSE.md | Complete worker handoff and limitations |

### Existing source and proposed future paths

The only inspected application source is source/treasury/routing.py. It is not modified. In a future separately authorized isolated workspace, a small explanation component may be proposed as source/treasury/explanation.py, with acceptance checks at tests/treasury/test_explanation.py and study materials at docs/treasury/pilot-protocol.md. These names are proposed task targets, not observed existing files. Endpoint, UI component, authentication, storage, and deployment paths must be decided during authorized design.

**Structure Decision**: Keep this attempt's deliverable in its artifacts directory. Do not run scaffold setup scripts that could mutate the supplied input tree or shared project state. Do not create a branch. Future task paths are relative to a separately authorized workspace; no task grants authority to edit this input bundle.

## Conditional Phases

### Phase 0 — Resolve authority and unanswered questions

After human requirements review and constitution resolution, collect decisions for Q1 vocabulary, Q2 mistaken-approval risk, and Q3 benefit measurement. Establish the real operator surface, runtime, access boundary, decision provenance source, historical decision retrieval, and performance/scale needs. Confirm who may approve requirements and separately who may authorize implementation and release.

Compare the existing flow and training/no-change alternative with the explanation proposal. Automatic approval remains rejected under current scope; any future proposal requires separate named policy approval and independent review. Do not use SRC-WIKI-OLD as an instruction source.

**Exit criteria**: Recorded human decisions, a ratified applicable constitution, and explicit authorization for design. Currently not met.

### Phase 1 — Candidate design for authorized human review

Propose a display contract that takes a trusted existing decision and presents route, reason, recorded policy_version, and a visible no-payment-approval notice. For REJECTED/INVALID_AMOUNT, explicitly report rejection without an eligibility recommendation. The contract must not create a payment capability.

Resolve handling of missing/unknown/mismatched provenance without fabricating a version or silently recalculating history. Define vocabulary and rendering on the selected surface. Decide whether any storage or operational logs are needed, including data minimization and access constraints, only after actual environment information is available. Re-evaluate the constitution after design.

**Exit criteria**: Human-reviewed design and explicit implementation authorization, with no policy changes. Currently BLOCKED.

### Phase 2 — Conditional implementation and engineering checks

If separately authorized, build the explanation presentation while leaving source/treasury/routing.py behavior unchanged. Use the fixed oracle as the expected-output source, not the implementation under test. Verify all eight SC-EXPL cases and the cross-cutting REQ-EXPL-002/004 invariants. Validate the exact threshold without rounding or floating-point reinterpretation.

Proposed evidence includes non-mutation of the decision, historical-version fidelity, no payment/fund-movement side effects, and invalid-input rejection without eligibility. Add explicit historical and missing-provenance examples only after the human decisions establish their supported behavior. No such tests or implementation ran here.

### Phase 3 — Limited observation and review

Only after a separately authorized safe alpha, observe consenting operations users on realistic tasks and compare with the current flow under the same task criteria. Measure correct-human-triage time and repeated clarification requests, with denominators and missing-data accounting. Determine sample size and thresholds before collecting outcomes.

Stop or redesign if users mistake routing for payment approval or if evidence is insufficient. Human accountability remains. The synthetic 12-case baseline cannot establish time savings or ROI. A later successful study does not itself authorize production release.

## Requirement-to-Work Traceability

| Requirement | Stories / scenarios | Proposed evidence and gate |
| --- | --- | --- |
| REQ-EXPL-001 | US1; SC-EXPL-001/002/003 | Exact route/reason/version and decision non-mutation |
| REQ-EXPL-002 | US1 and US2; all eight scenarios | Visible human-payment notice; no approval or fund movement; human interpretation review |
| REQ-EXPL-003 | US2; SC-EXPL-004/005/006/007 | Rejection/INVALID_AMOUNT without eligibility |
| REQ-EXPL-004 | US1 and US2; SC-EXPL-008 plus all versions | Recorded version fidelity and later approved historical examples |
| REQ-EXPL-005 | US3 | Hypothesis-only reporting and approved observation protocol |

## Complexity Tracking

No complexity exception is requested. The absence of ratified governance is a blocker, not an exception an agent can waive. A minimal presentation over a trusted existing decision is a proposal; platform and interface choices remain pending.

## Framework Application Record

Used the retained Spec Kit 1.2.2 spec, plan, and tasks template structures and read speckit-specify, speckit-plan, and speckit-tasks instructions. The supplied init metadata describes a Codex skills scaffold; this worker actually ran through ChatGPT collaboration and local tools. No native slash command or commercial CLI run is claimed.

No .specify/extensions.yml exists in the supplied input tree, so no registered hooks were found or run. Input-mutating setup scripts and feature registration were not executed under the task's read-only input constraint. The normal plan skill says to stop on unresolved clarifications; that readiness gate remains visibly blocked while this requested candidate is delivered for review.
