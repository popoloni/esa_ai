# B2: bounded intake and cooperative-provider classification

Owner: fictional Treasury service owner. Approved teaching contract (fictional case date) INTAKE/v1,
2025-05-20. evaluate_batch(requests, provider, *, max_attempts=2, max_calls=4) accepts
request_id/amount_eur records. It uses the retained B1 router and an injected
local cooperative provider returning {request_id,classification}; classifications
must be strings, MATCH or REVIEW. This exercise does not make a payment or authorize one.

Reject a numerically invalid amount before calling the provider. Each valid
request may use at most max_attempts calls, and the whole batch at most max_calls.
Retry ProviderUnavailable only. Preserve unexpected exceptions. A response must
have exactly the specified fields, match its request ID and use a known class;
otherwise raise ProviderProtocolError. A retry preserves request identity.
On exhaustion mark the request DEFERRED without inventing a provider response.
Successful records are CLASSIFIED with both route and provider classification.
Keep attempt number, identity and outcome in a receipt. Validate duplicate
request IDs across the whole submitted batch before any provider call; duplicates
raise ValueError with a zero-call receipt. Every exception retains its original
type and carries receipt, attempts, records and calls snapshots, including
previously completed records. An invalid response is an INVALID_RESPONSE attempt;
an unexpected provider exception is a PROVIDER_ERROR attempt and is not retried.
Both count as calls, so their cost remains attributable even though the batch
raises. These snapshots are local evidence, not a durable transaction ledger. This is not durable idempotency;
B3 introduces stored identity. Invocation bounds do not bound a blocking call's
wall-clock time: an untrusted external adapter needs a separate execution boundary.

All providers used by tests and demonstrations are deterministic local fixtures.
A request to auto-approve a payment, retry every exception or silently match a
response for another ID requires a different decision; the current specification
never permits those behaviors.
