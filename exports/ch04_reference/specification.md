# EXPLANATION-ONLY ALPHA — SPEC-004/v1

_Review candidate; not permission to implement or deploy._

## Authority
- Discovery: DISC-003/v1 (CONDITIONAL_GO_TO_LIMITED_ALPHA)
- Policy: BR-001/v1 — SRC-POL-001
- Owner: Product Owner (synthetic scenario)

## Scope
In: show_route, show_reason_code, show_policy_version, explicit_human_payment_boundary
Out: auto_approve, move_funds, change_threshold, alter_history, deploy_to_production

## Requirements
### REQ-EXPL-001: Explain the routing recommendation
For a valid routing decision the explanation MUST present route, reason code and policy version without altering the routing decision.
Sources: SRC-POL-001, SRC-OPS-004

### REQ-EXPL-002: Keep payment authorization separate
The explanation MUST explicitly say that a routing recommendation is not payment approval and that payment authorization remains a separate human process.
Sources: SRC-POL-001, SRC-RISK-002

### REQ-EXPL-003: Represent invalid requests safely
For invalid or non-positive amounts the explanation MUST report rejection and the INVALID_AMOUNT reason without creating an eligibility recommendation.
Sources: SRC-POL-001

### REQ-EXPL-004: Carry verified policy provenance
The explanation MUST display the policy version from the routing decision and MUST NOT silently infer a newer policy version or threshold.
Sources: SRC-POL-001

### REQ-EXPL-005: Do not present unvalidated benefit as fact
The alpha MUST treat time savings and user benefit as hypotheses pending observation and MUST NOT report a measured ROI before a field study.
Sources: SRC-OPS-004, SYN-TRIAGE-CSV

## Scenarios
### SC-EXPL-001: REQ-EXPL-001
**Given** BR-001/v1 routing-only service with a separate human payment authorization process
**When** an operator requests an explanation for amount 4999.99
**Then** return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

### SC-EXPL-002: REQ-EXPL-001
**Given** BR-001/v1 routing-only service with a separate human payment authorization process
**When** an operator requests an explanation for amount 5000
**Then** return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

### SC-EXPL-003: REQ-EXPL-001
**Given** BR-001/v1 routing-only service with a separate human payment authorization process
**When** an operator requests an explanation for amount 5000.01
**Then** return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

### SC-EXPL-004: REQ-EXPL-003
**Given** BR-001/v1 routing-only service with a separate human payment authorization process
**When** an operator requests an explanation for amount 0
**Then** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

### SC-EXPL-005: REQ-EXPL-003
**Given** BR-001/v1 routing-only service with a separate human payment authorization process
**When** an operator requests an explanation for amount -10
**Then** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

### SC-EXPL-006: REQ-EXPL-003
**Given** BR-001/v1 routing-only service with a separate human payment authorization process
**When** an operator requests an explanation for amount nonsense
**Then** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

### SC-EXPL-007: REQ-EXPL-003
**Given** BR-001/v1 routing-only service with a separate human payment authorization process
**When** an operator requests an explanation for amount NaN
**Then** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

### SC-EXPL-008: REQ-EXPL-004
**Given** BR-001/v1 routing-only service with a separate human payment authorization process
**When** an operator requests an explanation for amount 1
**Then** return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

## Open Questions
- Which explanation vocabulary do real operators understand?
- Does the interface accidentally induce payment approval?
- How will actual user benefit be measured in a pilot?

## Handoff
Ready for human requirements review only; design and production implementation not yet authorized.
