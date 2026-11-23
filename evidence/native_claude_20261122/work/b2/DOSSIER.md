# B2 decision record

## Expect

Contract INTAKE/v1 (docs/contract.md) is the only supplied contract; I found no conflict in it.
Outcome: `evaluate_batch(requests, provider, *, max_attempts=2, max_calls=4)` classifies
request_id/amount_eur records through the retained B1 `assess`, with bounded calls and a receipt.
It never authorizes payment (`payment_authorized` is always False).

Acceptance example: batch `[good(4000.00), bad(4000.00)]`, provider answers `good` correctly and
returns request_id `wrong` for `bad`. Expected: `ProviderProtocolError` (type preserved), `calls == 2`,
attempts `[good/1/MATCH, bad/1/INVALID_RESPONSE]`, `records` still holding the completed `good`.
A same-shape batch with a correct provider returns CLASSIFIED records instead.

Open owner question: the contract does not name record/receipt fields or validate
`max_attempts`/`max_calls` values (e.g. 0 or negative). I took field names from tests/test_b2.py
and did not invent a policy for odd bounds (0 simply means no calls and DEFERRED records).
Also unspecified: attempts for REJECTED requests (none are made) and the exact keys of
REJECTED/DEFERRED records (I used request_id, status, route, reason).

## Delegate

Only intake.py (was a NotImplementedError stub) and this file were edited. routing.py, tests, docs,
prior/ and READER_ENTRY.json were not touched. Implemented: duplicate-ID check over the whole batch before
any call (ValueError, zero calls); invalid amounts REJECTED without a provider call; retry of
ProviderUnavailable only (outcome UNAVAILABLE); per-request `max_attempts` and batch `max_calls`
with DEFERRED on exhaustion; strict response check (dict, exactly the two fields, matching ID,
str classification in MATCH/REVIEW) else INVALID_RESPONSE + ProviderProtocolError; any other provider
exception recorded as PROVIDER_ERROR (with error_type), counted, not retried, re-raised as the same
object. Every raised exception gets `receipt`, `attempts`, `records`, `calls` snapshots (deep copies).
Corrections: none needed after the first run (no failing iteration to explain).

## Observe

- `python3 -m unittest discover -s tests` -> Ran 12 tests, OK (one run, after implementation).
- An earlier shell command that wrote the file was refused by the tool's safety check; nothing ran. I
  then wrote the file with the file-edit tool.
- Not observed: protected acceptance, human approval, any behavior beyond the 12 supplied tests.
  Limits: no wall-clock bound on a blocking provider; snapshots are not a durable ledger; no durable
  idempotency (B3); the exception attributes require the exception to accept attribute assignment
  (true for ordinary exceptions; unverified for exotic ones); a TypeError from `assess` or a malformed
  request dict (missing key) also surfaces as an exception with snapshots, which the contract does not discuss.

## Decide

Proposals named in the task to ACCEPT/REJECT/ASK are not present in the supplied documents, so I cannot
assess them; the contract's own stated rules: auto-approving payment, retrying every exception, or matching
a response for another ID are REJECTED (require a different decision, not made here). Bound-validation
policy and the record keys above are ASK items for the owner. Handoff: intake.py plus this dossier,
ready for the operator's protected acceptance; human acceptance remains PENDING.
