# Requirements — explanation-only alpha

> Illustrative EARS-style mapping; review in Kiro before design.

## REQ-EXPL-001 Explain the routing recommendation
For a valid routing decision the explanation MUST present route, reason code and policy version without altering the routing decision.
WHEN an operator requests an explanation for amount 4999.99
THE SYSTEM SHALL return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

WHEN an operator requests an explanation for amount 5000
THE SYSTEM SHALL return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

WHEN an operator requests an explanation for amount 5000.01
THE SYSTEM SHALL return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

## REQ-EXPL-002 Keep payment authorization separate
The explanation MUST explicitly say that a routing recommendation is not payment approval and that payment authorization remains a separate human process.
## REQ-EXPL-003 Represent invalid requests safely
For invalid or non-positive amounts the explanation MUST report rejection and the INVALID_AMOUNT reason without creating an eligibility recommendation.
WHEN an operator requests an explanation for amount 0
THE SYSTEM SHALL return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

WHEN an operator requests an explanation for amount -10
THE SYSTEM SHALL return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

WHEN an operator requests an explanation for amount nonsense
THE SYSTEM SHALL return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

WHEN an operator requests an explanation for amount NaN
THE SYSTEM SHALL return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

## REQ-EXPL-004 Carry verified policy provenance
The explanation MUST display the policy version from the routing decision and MUST NOT silently infer a newer policy version or threshold.
WHEN an operator requests an explanation for amount 1
THE SYSTEM SHALL return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

## REQ-EXPL-005 Do not present unvalidated benefit as fact
The alpha MUST treat time savings and user benefit as hypotheses pending observation and MUST NOT report a measured ROI before a field study.
