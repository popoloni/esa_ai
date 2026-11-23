# B2 decision record

## Expect

Contract INTAKE/v1 (docs/contract.md, the only doc supplied). Outcome: `evaluate_batch` classifies
requests through the retained B1 `assess` router and an injected cooperative provider, within
`max_attempts`/`max_calls`, with attributable receipts. It never authorizes payment.

Discriminating acceptance example: two requests "a","b", provider always raises
`ProviderUnavailable`, `max_attempts=3, max_calls=2`. Expected: exactly 2 provider calls (both for "a"),
both records DEFERRED, "b" never called. A naive per-request-only bound would make 3 calls or give "b" calls.

Open owner question: the contract does not fix the record/attempt field layout beyond what tests assert.
I chose: record = request_id, status (REJECTED/CLASSIFIED/DEFERRED), route, reason, plus classification when
CLASSIFIED; attempt = request_id, attempt, outcome (MATCH/REVIEW/UNAVAILABLE/INVALID_RESPONSE/PROVIDER_ERROR,
plus error_type). The result also carries top-level attempts/calls/records/payment_authorized and a `receipt`
copy. A request starved by the global budget before any call is DEFERRED with no attempts. These are my
choices, not owner-approved. No conflict between documents was found.

## Delegate

Edited only `intake.py` (was `NotImplementedError`) and this file. `routing.py`, tests, docs, prior/ and
READER_ENTRY.json untouched. Behavior: duplicate IDs checked over the whole batch before any call (ValueError,
zero-call receipt); invalid amounts REJECTED with no call; only ProviderUnavailable retried; invalid response
(non-dict, extra/missing fields, wrong ID, non-string or unknown class) raises ProviderProtocolError without
retry; other provider exceptions are re-raised as the same object. Every raised exception gets
`receipt/attempts/records/calls` snapshots (deep copies, including earlier completed records).

## Observe

- Baseline `python3 -m pytest -q tests`: 18 failed (NotImplementedError), before any edit.
- After implementation: `python3 -m pytest -q tests` -> 12 passed, 6 subtests passed.
- Each correction maps to a baseline failure: every test failed from the stub; I implemented the contract rules
  above. No test was changed. No receipts from an external recorder were observed.
- `git status` also shows modified files under `../../companion/` that I did not touch; I did not examine them.

## Decide

Three proposals: none were supplied to me in the task or docs, so I cannot give ACCEPT/REJECT/ASK for them.
Contract-level standing decisions: auto-approving payment, retrying every exception and matching a response for
another ID are never permitted (not implemented). Handoff scope: the local invocation bounds only. Not
covered: wall-clock/blocking-call limits, durable idempotency (B3), a transaction ledger, and untested paths
such as malformed request dicts (missing keys raise KeyError with no receipt), non-hashable IDs, and
non-integer or negative bounds. Human acceptance remains PENDING; protected acceptance has not been run.
