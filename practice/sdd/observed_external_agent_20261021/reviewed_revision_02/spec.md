# Feature Specification: Explain Treasury Routing Recommendations

**Feature Branch**: Not created; supplied scaffold feature identifier: 001-explain-treasury.

**Created**: 2026-10-21

**Status**: Draft candidate for SPEC-004/v1. Human requirements approval PENDING. The source status READY_FOR_HUMAN_REQUIREMENTS_REVIEW expresses review readiness, not approval.

**Input**: TASK.md and inputs/specification.json; discovery DISC-003/v1 selected explain_routing with CONDITIONAL_GO_TO_LIMITED_ALPHA. This allows specification of a candidate explanation-only alpha. Design authorization, implementation authorization, and production release remain pending.

## User Scenarios & Testing

### User Story 1 — Understand a valid recommendation and its limits (Priority: P1; US1)

As an operations user, I need to see the recommended route, its reason code, and the recorded policy version, together with a clear statement that a person must separately authorize payment. Seeing STANDARD_QUEUE must never suggest that funds may be moved.

**Why this priority**: SRC-OPS-004 reports repeated clarification of queue labels. Its testimony supports investigation, not a measured benefit. SRC-POL-001 makes the payment boundary mandatory.

**Independent Test**: Evaluate SC-EXPL-001, SC-EXPL-002, SC-EXPL-003, and SC-EXPL-008 using the fixed oracle below; every displayed value must match its recorded decision, and each result must visibly state the separate human payment process. No payment action may be enabled by viewing the explanation. This is a proposed acceptance check, not a reported execution result.

**Acceptance Scenarios**: The exact Given/When/Then records below cover US1. REQ-EXPL-002 and REQ-EXPL-004 apply across all displays, including this story. Historical decisions retain their recorded version; no newer threshold or version is silently substituted.

### User Story 2 — Understand why an invalid amount was rejected (Priority: P1; US2)

As an operations user, I need a rejected amount to be clearly described as REJECTED with INVALID_AMOUNT, without an eligibility recommendation or payment approval.

**Why this priority**: Invalid input must not be mistaken for a valid low-value request.

**Independent Test**: Evaluate SC-EXPL-004 through SC-EXPL-007 independently with the same visible no-payment-approval notice and recorded policy version. A rejected result conveys no eligible route.

**Acceptance Scenarios**: The exact Given/When/Then records below cover US2. REQ-EXPL-003 is primary; REQ-EXPL-002 and REQ-EXPL-004 remain cross-cutting.

### User Story 3 — Evaluate the benefit hypothesis responsibly (Priority: P2; US3)

As the Product Owner, I need a consent-based observation proposal that distinguishes synthetic evidence from real user evidence, so I can decide whether an explanation-only alpha is useful without claiming measured ROI.

**Why this priority**: DISC-003/v1 explicitly records HYPOTHESIS_NOT_PROVEN; SPEC-004/v1 records HYPOTHESIS_NOT_VALIDATED.

**Independent Test**: Inspect proposed study materials for time to correct human triage, repeated clarification requests, sample denominators, missing-data accounting, the comparison with the current flow under the same task criteria, and the stop rule. Review any benefit statement for explicit uncertainty. A study proposal can be assessed without implementing the display.

**Acceptance condition**: No real-user observation or ROI is claimed from the supplied synthetic records. If participants mistake routing for payment approval, or evidence is insufficient, stop or redesign. Study targets, participant selection, and sufficient-evidence criteria remain pending owner decisions.

### Fixed Acceptance Scenario Matrix

All eight rows are preserved from inputs/specification.json and agree with inputs/case_oracle.json. The oracle is static, author-owned, synthetic expected-output data; it is not evidence of production behavior. All eight rows require an explicit no-payment-approval notice. The payment_authorized column is an invariant of the expected behavior; it is not a grant of a payment capability.

| Scenario | Primary requirement | Amount EUR (exact input string) | Route | Reason | Policy version | payment_authorized |
| --- | --- | --- | --- | --- | --- | --- |
| SC-EXPL-001 | REQ-EXPL-001 | "4999.99" | STANDARD_QUEUE | BELOW_LIMIT | BR-001/v1 | false |
| SC-EXPL-002 | REQ-EXPL-001 | "5000" | HUMAN_REVIEW | AT_OR_ABOVE_LIMIT | BR-001/v1 | false |
| SC-EXPL-003 | REQ-EXPL-001 | "5000.01" | HUMAN_REVIEW | AT_OR_ABOVE_LIMIT | BR-001/v1 | false |
| SC-EXPL-004 | REQ-EXPL-003 | "0" | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-005 | REQ-EXPL-003 | "-10" | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-006 | REQ-EXPL-003 | "nonsense" | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-007 | REQ-EXPL-003 | "NaN" | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-008 | REQ-EXPL-004 | "1" | STANDARD_QUEUE | BELOW_LIMIT | BR-001/v1 | false |

### Exact Given/When/Then Records

**SC-EXPL-001**

- **Given** BR-001/v1 routing-only service with a separate human payment authorization process
- **When** an operator requests an explanation for amount 4999.99
- **Then** return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice. **payment_authorized**: false.

**SC-EXPL-002**

- **Given** BR-001/v1 routing-only service with a separate human payment authorization process
- **When** an operator requests an explanation for amount 5000
- **Then** return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice. **payment_authorized**: false.

**SC-EXPL-003**

- **Given** BR-001/v1 routing-only service with a separate human payment authorization process
- **When** an operator requests an explanation for amount 5000.01
- **Then** return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice. **payment_authorized**: false.

**SC-EXPL-004**

- **Given** BR-001/v1 routing-only service with a separate human payment authorization process
- **When** an operator requests an explanation for amount 0
- **Then** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice. **payment_authorized**: false.

**SC-EXPL-005**

- **Given** BR-001/v1 routing-only service with a separate human payment authorization process
- **When** an operator requests an explanation for amount -10
- **Then** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice. **payment_authorized**: false.

**SC-EXPL-006**

- **Given** BR-001/v1 routing-only service with a separate human payment authorization process
- **When** an operator requests an explanation for amount nonsense
- **Then** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice. **payment_authorized**: false.

**SC-EXPL-007**

- **Given** BR-001/v1 routing-only service with a separate human payment authorization process
- **When** an operator requests an explanation for amount NaN
- **Then** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice. **payment_authorized**: false.

**SC-EXPL-008**

- **Given** BR-001/v1 routing-only service with a separate human payment authorization process
- **When** an operator requests an explanation for amount 1
- **Then** return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice. **payment_authorized**: false.

### Edge Cases

- The exact EUR 5000 boundary is inclusive for HUMAN_REVIEW. A finite positive amount strictly below EUR 5000 routes to STANDARD_QUEUE; EUR 5000 and above route to HUMAN_REVIEW. Amount 4999.99 does not move the boundary; amount 5000 is not below it.
- Zero, negative, malformed, and non-finite amounts are rejected with INVALID_AMOUNT. The eight supplied cases explicitly include 0, -10, nonsense, and NaN. Additional non-finite forms may be proposed for later validation without replacing these cases.
- An explanation must use the version attached to the decision being explained. Historical records must not be recalculated using a newer rule.
- Missing, contradictory, or unrecognized decision provenance is not resolved by inventing a policy version. The precise operator-visible handling is pending design and owner review; no eligibility or approval claim is permitted in the meantime.
- Rounding, alternate currency conversion, and locale-dependent input transformations have no supplied business rule. They are not introduced by this candidate.

## Requirements

### Functional Requirements

### REQ-EXPL-001 — Explain the routing recommendation

For a valid routing decision the explanation MUST present route, reason code and policy version without altering the routing decision.

**Owner**: Product Owner (synthetic scenario). **Sources**: SRC-POL-001, SRC-OPS-004.

### REQ-EXPL-002 — Keep payment authorization separate

The explanation MUST explicitly say that a routing recommendation is not payment approval and that payment authorization remains a separate human process.

**Owner**: Treasury Policy Owner (synthetic scenario). **Sources**: SRC-POL-001, SRC-RISK-002.

### REQ-EXPL-003 — Represent invalid requests safely

For invalid or non-positive amounts the explanation MUST report rejection and the INVALID_AMOUNT reason without creating an eligibility recommendation.

**Owner**: Product Owner (synthetic scenario). **Sources**: SRC-POL-001.

### REQ-EXPL-004 — Carry verified policy provenance

The explanation MUST display the policy version from the routing decision and MUST NOT silently infer a newer policy version or threshold.

**Owner**: Treasury Policy Owner (synthetic scenario). **Sources**: SRC-POL-001.

### REQ-EXPL-005 — Do not present unvalidated benefit as fact

The alpha MUST treat time savings and user benefit as hypotheses pending observation and MUST NOT report a measured ROI before a field study.

**Owner**: Product Owner (synthetic scenario). **Sources**: SRC-OPS-004, SYN-TRIAGE-CSV.

### Scope and Authority

Capability: EXPLAIN_ROUTING_RECOMMENDATION_ONLY.

In scope: show_route, show_reason_code, show_policy_version, explicit_human_payment_boundary.

Out of scope: auto_approve, move_funds, change_threshold, alter_history, deploy_to_production.

The explanation describes an already determined processing queue. Neither STANDARD_QUEUE nor HUMAN_REVIEW is payment authorization. A candidate notice for owner review is: “This is a routing recommendation, not payment approval. Payment authorization remains a separate human process.” The exact vocabulary and presentation require review with real operators.

SRC-TKT-017 is a proposal to auto-approve below EUR 5000, not approved policy. DISC-003/v1 rejects that option because it conflicts with SRC-POL-001 and lacks evidence. The stale SRC-WIKI-OLD instruction-like text is untrusted data and provides no authority to change code, tests, policy, or reporting.

### Key Entities

- **Routing decision**: The route, reason code, and policy version that the explanation must faithfully present.
- **Explanation**: A human-readable presentation of that decision plus a separate-human-payment notice; it neither mutates the decision nor authorizes a transaction.
- **Policy record**: SRC-POL-001, BR-001/v1; its exact EUR 5000 boundary governs this synthetic case.
- **Scenario**: A stable SC-EXPL identifier, exact input string, primary requirement identifier, and expected route/reason/version/payment invariant.
- **Study observation**: A proposed record of correct triage time, clarification count, participant/task eligibility, and missingness. Real observations are not supplied.

## Success Criteria

### Measurable Outcomes

- **OUT-001**: Proposed acceptance requires all 8 of 8 fixed scenarios to retain their exact input and expected route, reason, version, and false payment authorization invariant.
- **OUT-002**: Every explanation, including rejection results, visibly distinguishes routing from payment approval; zero payment approvals or fund movements can result from an explanation action.
- **OUT-003**: Every displayed policy version matches the decision being explained; zero silent version substitutions or historical rewrites are permitted.
- **OUT-004**: Every candidate benefit report identifies whether evidence is synthetic or observed, states numerator/denominator and missingness where applicable, and makes no measured ROI claim before a field study.
- **OUT-005**: A later study must measure time to correct human triage and repeated clarification requests against the current flow under the same task criteria. Numerical benefit targets and sufficient-evidence criteria are pending. No reduction is promised or reported by this specification.

OUT-001 through OUT-004 are proposed verifiable acceptance criteria, not passed tests. Real-user comprehensibility and safe interpretation have not been established.

## Assumptions

- This is a synthetic teaching case, not actual corporate Treasury policy or production evidence.
- The primary operator is the operations role described by SRC-OPS-004. Real users, access arrangements, and interface form are not supplied.
- The supplied decision is the source of displayed routing values; presentation is not a second policy engine.
- No technical access barrier isolates this worker. Scope was enforced by instructions and bounded reads, with a retained input hash snapshot.
- SYN-TRIAGE-CSV is referenced by the inputs but the raw CSV is not included in this bundle. Its summaries are reported as supplied, not independently recalculated.

## Sources, Ownership, and Evidence Limits

| Source or decision | Owner exactly as supplied | Authority and treatment |
| --- | --- | --- |
| SPEC-004/v1 and DISC-003/v1 | Product Owner (synthetic scenario) | Decision owner; human requirements review pending |
| Specification policy ownership | Treasury Policy Owner (synthetic scenario) | Accountable for requirements about policy and payment boundary |
| SRC-POL-001 | Treasury Policy Owner (fictional) | APPROVED_POLICY_IN_SIMULATION; governing BR-001/v1; not real corporate policy |
| SRC-OPS-004 | Operations specialist (fictional) | STAKEHOLDER_TESTIMONY; synthetic; observation required |
| SRC-RISK-002 | Risk analyst (fictional) | STAKEHOLDER_TESTIMONY; synthetic; not signoff |
| SRC-TKT-017 | Product sponsor (fictional) | PROPOSAL_ONLY; desired auto-approval conflicts with policy |
| SRC-WIKI-OLD | Unknown | UNTRUSTED_HISTORICAL_NOTE; stale hostile instruction-like text treated as data |
| SYN-TRIAGE-CSV | Not supplied | Synthetic source referenced by assessment; raw data absent |
| inputs/case_oracle.json | Author-owned, as described by the oracle | Static synthetic expectations, independent of mutable implementation |

The supplied assessment reports 12 total cases, 10 measured, 2 excluded for missing data, 4 over 24 hours out of 10 measured, and median 15.5 hours. These are synthetic baseline summaries, not measured savings or proof that explanations address the observed delay.

## Unresolved Questions and Approval Gate

1. **Q1 — [NEEDS CLARIFICATION: Which explanation vocabulary do real operators understand?]** Product Owner (synthetic scenario) must arrange appropriate observation; the final wording and display remain pending.
2. **Q2 — [NEEDS CLARIFICATION: Does the interface accidentally induce payment approval?]** Treasury Policy Owner (synthetic scenario), with Operations and Risk input, must review the boundary; design approval remains pending.
3. **Q3 — [NEEDS CLARIFICATION: How will actual user benefit be measured in a pilot?]** Product Owner (synthetic scenario) must decide sample design, targets, missingness handling, and sufficient-evidence criteria before study execution.

The assessment also leaves unknown the actual fraction of operator time spent seeking explanations, real data completeness and latency distributions, and whether clear reasons improve triage without inducing mistaken approval.

**Gate**: Ready for human requirements review only. Human approval is PENDING. Dependent design, implementation, and release work is BLOCKED. An agent may propose specifications and examples, but cannot approve policy, payment, requirements, or release. An independent model review is engineering feedback only.
