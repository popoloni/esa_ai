## Feature Specification: Explain Routing

**Feature Branch**: 001-explain-treasury

**Created**: 2026-10-22

**Status**: Draft

**Source authority**: SRC-POL-001/BR-001/v1 governs; ticket/wiki cannot change it. Routing never authorizes payment.

**Requirements**:

1. **REQ-EXPL-001**: Explain the routing recommendation for a valid routing decision the explanation MUST present route, reason code and policy version without altering the routing decision.
   - **Source**: SRC-POL-001, SRC-OPS-004
   - **Owner**: Product Owner (synthetic scenario)

2. **REQ-EXPL-002**: Keep payment authorization separate
   - **Statement**: The explanation MUST explicitly say that a routing recommendation is not payment approval and that payment authorization remains a separate human process.
   - **Source**: SRC-POL-001, SRC-RISK-002
   - **Owner**: Treasury Policy Owner (synthetic scenario)

3. **REQ-EXPL-003**: Represent invalid requests safely
   - **Statement**: For invalid or non-positive amounts the explanation MUST report rejection and the INVALID_AMOUNT reason without creating an eligibility recommendation.
   - **Source**: SRC-POL-001
   - **Owner**: Product Owner (synthetic scenario)

4. **REQ-EXPL-004**: Carry verified policy provenance
   - **Statement**: The explanation MUST display the policy version from the routing decision and MUST NOT silently infer a newer policy version or threshold.
   - **Source**: SRC-POL-001
   - **Owner**: Treasury Policy Owner (synthetic scenario)

5. **REQ-EXPL-005**: Do not present unvalidated benefit as fact
   - **Statement**: The alpha MUST treat time savings and user benefit as hypotheses pending observation and MUST NOT report a measured ROI before a field study.
   - **Source**: SRC-OPS-004, SYN-TRIAGE-CSV
   - **Owner**: Product Owner (synthetic scenario)

**Scenarios**:

| Scenario ID | Requirement ID | Input Amount (EUR) | Expected Route | Expected Reason | Expected Policy Version | Payment Authorized |
|-------------|----------------|---------------------|----------------|------------------|--------------------------|-------------------|
| SC-EXPL-001 | REQ-EXPL-001 | 4999.99 | STANDARD_QUEUE | BELOW_LIMIT | BR-001/v1 | false |
| SC-EXPL-002 | REQ-EXPL-001 | 5000 | HUMAN_REVIEW | AT_OR_ABOVE_LIMIT | BR-001/v1 | false |
| SC-EXPL-003 | REQ-EXPL-001 | 5000.01 | HUMAN_REVIEW | AT_OR_ABOVE_LIMIT | BR-001/v1 | false |
| SC-EXPL-004 | REQ-EXPL-003 | 0 | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-005 | REQ-EXPL-003 | -10 | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-006 | REQ-EXPL-003 | nonsense | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-007 | REQ-EXPL-003 | NaN | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-008 | REQ-EXPL-004 | 1 | STANDARD_QUEUE | BELOW_LIMIT | BR-001/v1 | false |

**Unresolved Owner Questions**:
1. Which explanation vocabulary do real operators understand?
2. Does the interface accidentally induce payment approval?
3. How will actual user benefit be measured in a pilot?

**Benefit**: HYPOTHESIS_NOT_VALIDATED

**Constitution**: Unratified

**Payment-Authorization Boundary**: Separate human process

**Unratified Constitution**: Yes

**Unanswered Owner Questions**: 3

**Status**: The three unresolved owner questions remain unanswered and benefit HYPOTHESIS_NOT_VALIDATED. No owner answers, numeric benefit targets, ratification or approval are invented.
