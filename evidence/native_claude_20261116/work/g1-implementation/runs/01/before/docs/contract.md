# RES-001/v1 — approved teaching contract (synthetic)

## Authority and scope
The fictional workshop coordinator owns the rules. The first slice is **exclusive equipment reservation**, not payment, real-world access control, capacity pooling, cancellation, notification, or a waiting list. No physical assets or live users are involved.

## Capability
For a trusted member identity (provided by the authenticated calling boundary), asset identifier, UTC start and UTC end, confirm one reservation if the requested interval does not overlap another confirmed interval for that asset.

- Timestamps: canonical `YYYY-MM-DDTHH:MM:SSZ`; UTC; second precision. Start is strictly before end. Maximum duration is 24 hours.
- Interval semantics: half-open `[start, end)`. Overlap if `existing.start < request.end AND request.start < existing.end`.
- Identity: the request itself must not supply a member id. A **trusted caller** supplies `trusted_member_id`. This demonstration does not implement or verify authentication.
- Idempotency scope: `(trusted_member_id, idempotency_key)`. A retry of an identical request returns the same reservation id, with status 200 and `replayed=True`; reusing a key for another request returns 409.
- New reservation: status 201, code `confirmed`, one durable record.
- Overlap: status 409, code `interval-conflict`, no additional record.
- Invalid input: status 422, no record.
- Atomicity: the check and insert occur in one protected transaction; concurrent requests for the same free slot must not both confirm.
- Caller provides a path to a local SQLite database. This is not a service API or production authorization implementation.

## Independent scenarios
Given an empty asset A, when member 1 requests 09:00–10:00, then a new reservation is confirmed.
Given A reserved 09:00–10:00, when member 2 requests 09:30–10:30, then 409 and no added record.
Given A reserved 09:00–10:00, when member 2 requests 10:00–11:00, then confirmation (adjacency).
Given member 1 repeats the original request with the original key, then the reservation ID stays unchanged and row count is one.
Given member 1 reuses its original key for a changed interval, then 409 and no added record.
Given two simultaneous independent requests against the same empty asset and slot, then at most one confirmation.

## Explicit exclusions
No production identity provider, HTTP endpoint, tenant authorization, rate limiting, migrations, cancellation, telemetry, recovery tooling or load/performance guarantee. A local green test suite is not deployment approval.
