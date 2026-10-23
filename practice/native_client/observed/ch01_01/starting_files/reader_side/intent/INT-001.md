# INT-001: reject non-positive and malformed routing amounts

- **Business decision owner (synthetic):** Operations policy owner
- **Recorded decision:** BR-001/v1 amendment for input validation only
- **Intended behavior:** An amount must be a finite, parseable decimal strictly greater than zero to be routed. For zero, negative, nonnumeric or nonfinite values return `REJECTED / INVALID_AMOUNT`.
- **Preserve:** Positive values strictly below EUR 5,000 use `STANDARD_QUEUE / BELOW_LIMIT`. Values at or above EUR 5,000 use `HUMAN_REVIEW / AT_OR_ABOVE_LIMIT`.
- **Non-goals:** No change to the EUR 5,000 threshold; no payments, ledger, API, DB or historical replay in Chapter 1.
- **Authority:** The agent may propose code; it cannot revise this decision.
- **Acceptance:** External acceptance cases pass without changes to `acceptance/`. A human reviews the diff and records the verdict.
- **Limitation:** This policy was invented for the educational case; it is not a real Treasury policy.
