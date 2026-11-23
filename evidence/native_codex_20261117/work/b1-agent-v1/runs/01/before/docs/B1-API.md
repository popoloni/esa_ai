# B1-API/v1: Python boundary and current checks

Owner: fictional Treasury API maintainer. Status: approved teaching contract (fictional case date).
Fictional case effective date: 2025-05-14. This type/error obligation was added after the
recorded model edit of 2026-10-22; it is not attributed to that earlier run.

BR-001/v1 remains the business rule: reject malformed, nonfinite and nonpositive
amounts; route positive finite values below EUR 5,000 to STANDARD_QUEUE and values
at or above the boundary to HUMAN_REVIEW. `docs/BR-001.md` governs that rule.

The Python API is `assess(amount_eur: str) -> RoutingDecision`.
`RoutingDecision` is a dataclass with `route`, `reason`, `policy_version`.
A non-string argument is a caller programming error: raise `TypeError` explicitly.
Only `decimal.InvalidOperation` from conversion becomes REJECTED/INVALID_AMOUNT.
Unexpected errors, including an injected RuntimeError, must propagate. Check
finiteness before an ordered Decimal comparison so NaN and sNaN are rejected.

The seven core cases remain byte-for-byte unchanged. Five additional
protected public methods cover Infinity, -Infinity, inf, sNaN, and non-string
caller arguments. The default and continuation checks therefore run twelve methods.

A separate review probe injects RuntimeError into the known Decimal binding of
the supplied candidate packs. It demonstrates why a catch-all can pass twelve
ordinary cases yet hide an unexpected failure. This probe is not a universal
acceptance gate: another correct implementation may put conversion elsewhere.
Review its actual exception boundary and design an appropriate fault observation.
The review exercise explicitly covers the known catch-all gap; a passing public
suite alone does not establish every exception path.

BR-001 does not impose a narrow lexical grammar on valid strings. Current
conversion therefore accepts `1e3` and `4_000`; the library also accepts whitespace,
signs and other Decimal-supported forms. If the owner wants a stricter monetary
format, record a requirements decision first and derive new expectations from it.
The versioned follow-up owner decision resolves the grammar question; it does not invent
an ASCII-only, two-decimal-place rule.
