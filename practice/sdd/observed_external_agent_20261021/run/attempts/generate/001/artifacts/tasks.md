# Tasks: Explain Treasury Routing Recommendations

**Input**: Candidate spec.md and plan.md in this attempt's artifacts directory, plus the fixed input bundle.

**Prerequisites**: Human requirements approval, ratified applicable constitution, and separately authorized design/implementation are NOT present. All tasks below are pending. No checkbox indicates work completed, approval, deployment, or a passed acceptance test.

**Organization**: Spec Kit 1.2.2 phase and story structure, adapted to a review-only candidate. Format is checkbox, sequential task ID, optional parallel marker, optional story label, and a concrete file path.

**Path conventions**: Existing inputs remain immutable. Review paths below and future source/test/docs paths are proposed locations in a separately authorized isolated workspace, not permission to modify this input bundle or overwrite this first attempt. Future corrections must preserve this attempt and use a new revision.

**Test scope**: The specification explicitly defines acceptance checks. Related tests below are proposed future verification work, not tests executed in this generation task.

## Phase 1: Setup — Human Review Preparation

- [ ] T001 Prepare a human review packet at reviews/treasury/requirements-packet.md linking the retained artifacts/spec.md, all five REQ-EXPL IDs, all eight SC-EXPL IDs, source ownership, and pending Q1/Q2/Q3; retain the first candidate unchanged.
- [ ] T002 Record the actual Product Owner (synthetic scenario) and Treasury Policy Owner (synthetic scenario) requirements decisions at reviews/treasury/requirements-decision.json only when supplied by those humans; leave approval pending otherwise. Depends on T001.
- [ ] T003 Obtain applicable ratified governance and record its owner, version, and actual ratification evidence at reviews/treasury/constitution-decision.md; do not fill .specify/memory/constitution.md by guessing. Depends on T002.

**Checkpoint**: Human requirements and constitution gates remain pending; agents cannot self-approve T002 or T003.

## Phase 2: Foundational — Blockers Before Any Implementation

- [ ] T004 Resolve the actual runtime, interface surface, trusted decision source, historical retrieval, access boundary, scale, and performance questions in reviews/treasury/design-inputs.md after explicit design authorization. Depends on T002 and T003.
- [ ] T005 Define the proposed display contract in docs/treasury/explanation-contract.md with unchanged route, reason, recorded policy_version, visible separate-human-payment notice, and rejection without eligibility; record missing-provenance behavior only after owner decision. Depends on T004.
- [ ] T006 Obtain the human design decision and explicit implementation authorization at reviews/treasury/design-decision.json, including a fresh constitution check; record missing authorization as BLOCKED. Depends on T005.

**Checkpoint**: T006 blocks every application test-writing or implementation task below. Preparation of this task list does not satisfy it. Every story must maintain the payment boundary even if delivered independently.

## Phase 3: User Story 1 — Valid Recommendation With Explicit Limits (Priority: P1)

**Goal**: Show the decision and its policy provenance without granting payment authority.

**Independent Test**: SC-EXPL-001, SC-EXPL-002, SC-EXPL-003, and SC-EXPL-008 must match the fixed oracle and display the separate-human-payment notice. Historical versions must not be replaced.

- [ ] T007 [US1] Create the approved acceptance examples in tests/treasury/test_explanation.py from SC-EXPL-001 (4999.99/STANDARD_QUEUE/BELOW_LIMIT), SC-EXPL-002 (5000/HUMAN_REVIEW/AT_OR_ABOVE_LIMIT), SC-EXPL-003 (5000.01/HUMAN_REVIEW/AT_OR_ABOVE_LIMIT), and SC-EXPL-008 (1/STANDARD_QUEUE/BELOW_LIMIT), with BR-001/v1 and payment_authorized false in each case. Depends on T006.
- [ ] T008 [US1] Add non-mutation, recorded-version, explicit notice, and absence-of-payment-side-effect checks to tests/treasury/test_explanation.py; add historical/provenance examples only from the approved contract, not invented expected versions. Depends on T007.
- [ ] T009 [US1] Run the new tests and retain the observed pre-implementation result at reviews/treasury/us1-before-implementation.txt; distinguish an expected missing-feature failure from setup errors, and report if tests already pass. Depends on T008.
- [ ] T010 [US1] Implement only the authorized explanation presentation in source/treasury/explanation.py using the existing decision, without duplicating threshold logic, mutating source/treasury/routing.py, changing BR-001/v1, or creating a payment capability. Depends on T009 and continued T006 authorization.
- [ ] T011 [US1] Record scenario results, policy provenance fidelity, and a human-reviewed display example at reviews/treasury/us1-evidence.md; leave interpretation approval pending until a human supplies it. Depends on T010.

**Checkpoint**: US1 is technically testable alone after the foundation, but real-user interpretation remains an independent human gate. Its initial valid-amount demonstration is not a safe complete alpha for arbitrary amounts.

## Phase 4: User Story 2 — Invalid Request Rejection (Priority: P1)

**Goal**: Explain rejection without creating an eligibility recommendation.

**Independent Test**: SC-EXPL-004 through SC-EXPL-007 must each yield REJECTED/INVALID_AMOUNT/BR-001/v1, payment_authorized false, and the separate-human-payment notice.

- [ ] T012 [US2] Add SC-EXPL-004 (0), SC-EXPL-005 (-10), SC-EXPL-006 (nonsense), and SC-EXPL-007 (NaN) to tests/treasury/test_explanation.py with exact REJECTED/INVALID_AMOUNT/BR-001/v1 expectations, false payment authorization, and no eligibility recommendation. Depends on T006; coordinate shared-file edits after T011 in the proposed execution order.
- [ ] T013 [US2] Run the rejection acceptance checks before changing behavior and retain actual outcomes at reviews/treasury/us2-before-implementation.txt; do not label a test as failing without observing it. Depends on T012.
- [ ] T014 [US2] Implement the approved rejection presentation in source/treasury/explanation.py without recalculating routing or adding payment actions; preserve US1 behavior. Depends on T013 and continued T006 authorization.
- [ ] T015 [US2] Record independent rejection checks and all-eight-scenario regression results at reviews/treasury/us2-evidence.md, including visible notices and non-mutation evidence. Depends on T014.

**Checkpoint**: Both P1 stories and all eight fixed scenarios are required before proposing an alpha that accepts the supplied range of inputs. US2 is independently testable with rejected decisions; the execution sequence above avoids shared-file conflicts.

## Phase 5: User Story 3 — Benefit Hypothesis and Safe Observation (Priority: P2)

**Goal**: Produce a reviewable observation protocol without claiming demonstrated benefit.

**Independent Test**: Protocol review can verify the same-task comparison, metrics, denominators, missingness, consent, hypotheses, and stop rule without relying on application implementation.

- [ ] T016 [US3] Draft docs/treasury/pilot-protocol.md with current-flow comparison, time to correct human triage, repeated clarification requests, consent, numerator/denominator and missing-data accounting, Q1/Q2/Q3, and the exact stop-or-redesign condition for mistaken approval or insufficient evidence. Depends on T002 and T003; execution remains blocked.
- [ ] T017 [US3] Record human decisions on vocabulary, mistaken-approval checks, participant/task selection, sample size, numerical targets, sufficient-evidence criteria, and study authorization at reviews/treasury/pilot-decision.json; do not infer approval from model feedback. Depends on T016.
- [ ] T018 [US3] Prepare a clearly labeled blank observation and benefit-report form at docs/treasury/pilot-results-template.md that separates supplied synthetic baseline summaries from future real observations and forbids measured ROI claims before a field study. Depends on T017.
- [ ] T019 [US3] Conduct the study only after explicit human study authorization and a separately approved safe alpha, then record actual observations and stop-rule outcomes at reviews/treasury/pilot-observations.md; leave this task blocked if no authorization or real observations exist. Depends on T011, T015, T017, and T018.

**Checkpoint**: A hypothesis remains unvalidated until actual evidence is reviewed. A technical pass or small synthetic sample cannot approve benefit or production release.

## Phase 6: Review and Cross-Cutting Gates

- [ ] T020 Have an independent reviewer check all five requirements, all eight exact scenarios, source authority, and task dependencies; retain findings at reviews/treasury/independent-engineering-review.md. Depends on the relevant candidate/evidence being available; model review has no business approval authority.
- [ ] T021 Obtain and record the accountable human alpha decision at reviews/treasury/alpha-decision.json after reviewing Q1/Q2, US1/US2 engineering evidence, and applicable policy constraints; unresolved mistaken-approval risk keeps the alpha blocked. Depends on T011, T015, T017, and T020.
- [ ] T022 Record the release disposition at reviews/treasury/release-decision.json as BLOCKED unless a separately authorized human release process is actually completed. No deployment task is included or authorized; neither alpha approval nor benefit evidence is production release approval.

## Dependencies & Execution Order

The human requirements and constitution gate is T001 → T002 → T003. Authorized design proceeds T004 → T005 → T006. US1 is T007 → T008 → T009 → T010 → T011. US2 is T012 → T013 → T014 → T015. The sequence schedules US2 after US1 to avoid shared-file conflicts, while its rejection behavior can be independently exercised against rejected decisions.

US3 protocol preparation begins after T002/T003 and is independent of coding; T016 → T017 → T018. Study execution T019 additionally requires T021, so the alpha gate must be passed before any study runs. T020 reviews available candidate and implementation evidence without approving it. T021 follows completed P1 evidence, T017, and T020. T022 remains a separate human process and authorizes no deployment in this task list.

No [P] flags are assigned to tasks with presently unmet gates. After the gates are actually met, US3 protocol drafting and US1 engineering work use different files and may run concurrently. US1 and US2 edits to the same source/test files are serialized. Within US1, an independently assigned reviewer can inspect source authority while the developer prepares tests, provided the review never becomes approval. Within US2, independent inspection of rejection wording can occur alongside test execution, but both must finish before its evidence is accepted. Within US3, study-design and evidence-report reviews may run independently after their respective documents exist; final authorization remains with humans.

## Implementation Strategy

For this attempt the complete deliverable is the candidate spec, conditional plan, task list, and provenance; no listed implementation task runs.

A later technical demonstration may start with US1 after authorization. A safe limited alpha must include US2 rejection behavior, all eight fixed scenarios, the payment boundary, approved vocabulary, and the human alpha decision. US3 supplies the evaluation protocol and cannot claim a validated benefit before observation. Production release remains outside the authorized scope.

## Completion Accounting

22 pending tasks: 6 setup/foundational, 5 US1, 4 US2, 4 US3, and 3 cross-cutting. All task entries use the required unchecked checklist format with sequential IDs and explicit file paths. No task has been marked complete. Future source paths are proposals, not existing implementation claims.
