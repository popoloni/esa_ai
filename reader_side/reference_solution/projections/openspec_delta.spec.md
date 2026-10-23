# EXPLANATION-ONLY CHANGE — ILLUSTRATIVE DRAFT

## ADDED Requirements

### Requirement: Explain the routing recommendation
For a valid routing decision the explanation MUST present route, reason code and policy version without altering the routing decision.

#### Scenario: SC-EXPL-001
- **GIVEN** BR-001/v1 routing-only service with a separate human payment authorization process
- **WHEN** an operator requests an explanation for amount 4999.99
- **THEN** return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

#### Scenario: SC-EXPL-002
- **GIVEN** BR-001/v1 routing-only service with a separate human payment authorization process
- **WHEN** an operator requests an explanation for amount 5000
- **THEN** return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

#### Scenario: SC-EXPL-003
- **GIVEN** BR-001/v1 routing-only service with a separate human payment authorization process
- **WHEN** an operator requests an explanation for amount 5000.01
- **THEN** return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

### Requirement: Keep payment authorization separate
The explanation MUST explicitly say that a routing recommendation is not payment approval and that payment authorization remains a separate human process.

### Requirement: Represent invalid requests safely
For invalid or non-positive amounts the explanation MUST report rejection and the INVALID_AMOUNT reason without creating an eligibility recommendation.

#### Scenario: SC-EXPL-004
- **GIVEN** BR-001/v1 routing-only service with a separate human payment authorization process
- **WHEN** an operator requests an explanation for amount 0
- **THEN** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

#### Scenario: SC-EXPL-005
- **GIVEN** BR-001/v1 routing-only service with a separate human payment authorization process
- **WHEN** an operator requests an explanation for amount -10
- **THEN** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

#### Scenario: SC-EXPL-006
- **GIVEN** BR-001/v1 routing-only service with a separate human payment authorization process
- **WHEN** an operator requests an explanation for amount nonsense
- **THEN** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

#### Scenario: SC-EXPL-007
- **GIVEN** BR-001/v1 routing-only service with a separate human payment authorization process
- **WHEN** an operator requests an explanation for amount NaN
- **THEN** return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

### Requirement: Carry verified policy provenance
The explanation MUST display the policy version from the routing decision and MUST NOT silently infer a newer policy version or threshold.

#### Scenario: SC-EXPL-008
- **GIVEN** BR-001/v1 routing-only service with a separate human payment authorization process
- **WHEN** an operator requests an explanation for amount 1
- **THEN** return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

### Requirement: Do not present unvalidated benefit as fact
The alpha MUST treat time savings and user benefit as hypotheses pending observation and MUST NOT report a measured ROI before a field study.

