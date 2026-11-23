# B1-API/v2: explicit monetary-text grammar

Owner: fictional Treasury API maintainer with the workshop rule owner.
Status: approved teaching decision B1-OD-02. Fictional case decision date: 2025-05-20.
Supersedes B1-API/v1 only in the separately created v2 working copy.
The numeric business rule and returned policy identifier remain BR-001/v1.

The Python function remains `assess(amount_eur: str) -> RoutingDecision`.
Non-string input raises `TypeError`. Unexpected internal exceptions propagate.

Accept syntax matching `[+-]?[0-9]+(?:\.[0-9]{1,2})?`, at most 32 characters
including a sign or decimal point. Digits must be ASCII. Leading zeros and a
leading plus sign are permitted. A minus sign is syntactically permitted, but
negative values and both positive and negative zero are numerically rejected.
One or two fractional digits are allowed. Leading/trailing decimal points,
spaces, commas, underscores, exponent notation and non-ASCII digits are rejected.
Nonfinite spellings are rejected. No rounding or silent normalization occurs.

Examples admitted by syntax: `4000`, `004000.00`, `+4999.99`, `5000.0`, `-1.00`.
The last is rejected by the numeric rule. Examples rejected by syntax: `1e3`,
`4_000`, ` 4000`, `.50`, `5000.`, `4999.995`, `4.000,00`, and `４０００`.
After syntax validation, use exact decimal arithmetic. A finite positive value
below 5000 goes to STANDARD_QUEUE/BELOW_LIMIT; 5000 or above goes to
HUMAN_REVIEW/AT_OR_ABOVE_LIMIT. All invalid inputs return
REJECTED/INVALID_AMOUNT with policy_version BR-001/v1.

Evidence under v1 remains a record of v1. The float counterexamples with many
fractional digits or exponent notation are outside v2; do not reuse them as
if they proved the same defect under this changed grammar. Add new v2 checks,
rerun the current gate, and preserve the v1 working copy and receipts.

Use fullmatch for the entire input. A pattern ending in $ can match before a
final newline; [0-9] deliberately excludes Unicode digits that Python \d accepts.
HISTORY-API/v1 later uses its own narrower storage grammar: optional minus only,
1–12 integer digits, up to two fractional digits, no leading plus. Its canonical
identity removes leading zeros and supplies two fractional digits. These are two
named API contracts, not two interchangeable spellings of one regular expression.

Synthetic changed-source control.
