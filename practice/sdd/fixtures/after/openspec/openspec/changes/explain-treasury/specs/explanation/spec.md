# Explanation capability delta

AUTHOR_EXERCISE — authored teaching artifacts, not output from a live named coding-agent client.

## Review boundary

Status: READY_FOR_HUMAN_REQUIREMENTS_REVIEW
Contract: SPEC-004/v1
Discovery: DISC-003/v1 — CONDITIONAL_GO_TO_LIMITED_ALPHA
Policy: BR-001/v1
Policy authority: SRC-POL-001
Decision owner: Product Owner (synthetic scenario)
Policy owner: Treasury Policy Owner (synthetic scenario)
Value status: HYPOTHESIS_NOT_VALIDATED
Out of scope: auto_approve, move_funds, change_threshold, alter_history, deploy_to_production

This is an explanation-only proposal. Design and task documents describe candidate work,
not authorization to implement or release. All people, policy and data are synthetic.

## Unresolved questions

- Which explanation vocabulary do real operators understand?
- Does the interface accidentally induce payment approval?
- How will actual user benefit be measured in a pilot?

## ADDED Requirements

### Requirement: REQ-EXPL-001 — Explain the routing recommendation

For a valid routing decision the explanation MUST present route, reason code and policy version without altering the routing decision.

Sources: SRC-POL-001, SRC-OPS-004
Owner: Product Owner (synthetic scenario)

#### Scenario: SC-EXPL-001
- **GIVEN** BR-001/v1 routing-only service; payment authorization is a separate human process.
- **WHEN** amount_eur = `4999.99`
- **THEN** route = `STANDARD_QUEUE`; reason = `BELOW_LIMIT`; policy = `BR-001/v1`; payment_authorized = `false`; notice = `ROUTING_ONLY_NOT_PAYMENT_APPROVAL`.
- Requirement: REQ-EXPL-001

#### Scenario: SC-EXPL-002
- **GIVEN** BR-001/v1 routing-only service; payment authorization is a separate human process.
- **WHEN** amount_eur = `5000`
- **THEN** route = `HUMAN_REVIEW`; reason = `AT_OR_ABOVE_LIMIT`; policy = `BR-001/v1`; payment_authorized = `false`; notice = `ROUTING_ONLY_NOT_PAYMENT_APPROVAL`.
- Requirement: REQ-EXPL-001

#### Scenario: SC-EXPL-003
- **GIVEN** BR-001/v1 routing-only service; payment authorization is a separate human process.
- **WHEN** amount_eur = `5000.01`
- **THEN** route = `HUMAN_REVIEW`; reason = `AT_OR_ABOVE_LIMIT`; policy = `BR-001/v1`; payment_authorized = `false`; notice = `ROUTING_ONLY_NOT_PAYMENT_APPROVAL`.
- Requirement: REQ-EXPL-001

### Requirement: REQ-EXPL-002 — Keep payment authorization separate

The explanation MUST explicitly say that a routing recommendation is not payment approval and that payment authorization remains a separate human process.

Sources: SRC-POL-001, SRC-RISK-002
Owner: Treasury Policy Owner (synthetic scenario)

#### Scenario: SC-AUTH-ALL
- **WHEN** any valid or rejected explanation is presented
- **THEN** it states that routing is not payment approval; human payment authorization remains separate.

### Requirement: REQ-EXPL-003 — Represent invalid requests safely

For invalid or non-positive amounts the explanation MUST report rejection and the INVALID_AMOUNT reason without creating an eligibility recommendation.

Sources: SRC-POL-001
Owner: Product Owner (synthetic scenario)

#### Scenario: SC-EXPL-004
- **GIVEN** BR-001/v1 routing-only service; payment authorization is a separate human process.
- **WHEN** amount_eur = `0`
- **THEN** route = `REJECTED`; reason = `INVALID_AMOUNT`; policy = `BR-001/v1`; payment_authorized = `false`; notice = `ROUTING_ONLY_NOT_PAYMENT_APPROVAL`.
- Requirement: REQ-EXPL-003

#### Scenario: SC-EXPL-005
- **GIVEN** BR-001/v1 routing-only service; payment authorization is a separate human process.
- **WHEN** amount_eur = `-10`
- **THEN** route = `REJECTED`; reason = `INVALID_AMOUNT`; policy = `BR-001/v1`; payment_authorized = `false`; notice = `ROUTING_ONLY_NOT_PAYMENT_APPROVAL`.
- Requirement: REQ-EXPL-003

#### Scenario: SC-EXPL-006
- **GIVEN** BR-001/v1 routing-only service; payment authorization is a separate human process.
- **WHEN** amount_eur = `nonsense`
- **THEN** route = `REJECTED`; reason = `INVALID_AMOUNT`; policy = `BR-001/v1`; payment_authorized = `false`; notice = `ROUTING_ONLY_NOT_PAYMENT_APPROVAL`.
- Requirement: REQ-EXPL-003

#### Scenario: SC-EXPL-007
- **GIVEN** BR-001/v1 routing-only service; payment authorization is a separate human process.
- **WHEN** amount_eur = `NaN`
- **THEN** route = `REJECTED`; reason = `INVALID_AMOUNT`; policy = `BR-001/v1`; payment_authorized = `false`; notice = `ROUTING_ONLY_NOT_PAYMENT_APPROVAL`.
- Requirement: REQ-EXPL-003

### Requirement: REQ-EXPL-004 — Carry verified policy provenance

The explanation MUST display the policy version from the routing decision and MUST NOT silently infer a newer policy version or threshold.

Sources: SRC-POL-001
Owner: Treasury Policy Owner (synthetic scenario)

#### Scenario: SC-EXPL-008
- **GIVEN** BR-001/v1 routing-only service; payment authorization is a separate human process.
- **WHEN** amount_eur = `1`
- **THEN** route = `STANDARD_QUEUE`; reason = `BELOW_LIMIT`; policy = `BR-001/v1`; payment_authorized = `false`; notice = `ROUTING_ONLY_NOT_PAYMENT_APPROVAL`.
- Requirement: REQ-EXPL-004

### Requirement: REQ-EXPL-005 — Do not present unvalidated benefit as fact

The alpha MUST treat time savings and user benefit as hypotheses pending observation and MUST NOT report a measured ROI before a field study.

Sources: SRC-OPS-004, SYN-TRIAGE-CSV
Owner: Product Owner (synthetic scenario)

#### Scenario: SC-BENEFIT-UNKNOWN
- **WHEN** the alpha describes its expected benefit before any user study
- **THEN** the benefit remains a hypothesis and no measured ROI is reported.

