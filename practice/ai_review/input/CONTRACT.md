# Review contract

These are independent proposed snippets, not a single combined package. C01 and
C02 implement assess(amount_eur: str). For finite positive decimal strings, a
value below EUR 5,000 is STANDARD_QUEUE/BELOW_LIMIT; equality and greater values
are HUMAN_REVIEW/AT_OR_ABOVE_LIMIT. Invalid, nonfinite and nonpositive strings
are REJECTED/INVALID_AMOUNT. Their policy identity is BR-001/v1. These functions
recommend a queue and do not authorize payment. Inputs outside strings are not
part of this exercise.

C03, C04 and C05 implement present(decision), accepting a decision mapping with
route, reason_code and policy_version. Preserve these three values exactly and
add payment_authorized=False. The mapping can represent a saved historical v1
record or a new v2 record; the presenter must not recalculate or relabel its
policy. No particular style or data-copy implementation is required.

For each case report actionable correctness defects against this contract, with
line/behavior and a discriminating input. If no contract defect is found, say so.
Separate uncertain observations from findings. Do not expand scope to deployment,
HTTP authentication or claims about arbitrary object types not in the contract.
