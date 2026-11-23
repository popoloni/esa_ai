# G4: diagnosis and accepted-outcome accounting

Owner: fictional operations lead. Approved teaching contract (fictional case date) OPS-G4/v2,
2025-05-22. This diagnostic adapter explicitly targets the known G3 schema 3;
it is not a schema-independent acceptance check for arbitrary reservation designs.

Version2 explicitly recognizes two retained schema3 representations. The reference
`reservations` table has columns id, asset_id, member_id, starts_at, ends_at,
request_key, request_hash, state, version. The recorded progressive
`reservations_v2` table has columns reservation_id, trusted_member_id, asset_id,
starts_at, ends_at, idempotency_key, payload_fingerprint, state, version.
Match the complete signature and use the corresponding ID column. The current
recorded table can coexist with original historical tables, which must not be
counted as current reservations. Refuse unsupported or competing current
representations; do not guess a mapping from user_version alone. This explicit
teaching-case extension was authored on 16 November 2026 for the actual retained
G3 candidate. It does not certify an arbitrary schema3 database.

Implement diagnose(path) as a read-only observation of existing storage. Report
state counts, pairs of overlapping active reservations on the same asset, schema
version, resolved path and a digest. Exclude cancelled reservations and adjacency.
Do not repair, delete or initialize data. Refuse missing/unsupported storage.
Record unchanged bytes before/after; detect concurrent modification rather than
silently claiming a stable snapshot. The owner supplies deliberately corrupted
synthetic fixtures to exercise diagnosis; no production incident is represented.

Implement cost_summary(attempts,accepted). Every attempt supplies cost_eur and
minutes, including failed generations, review and recovery. Sum all finite,
nonnegative values with Decimal. Nonnumeric, nonfinite and negative cost or time
values raise ValueError; malformed numeric text is not silently zero. The denominator is accepted outcomes supplied
by a separate decision, not tests passed or attempts made. Report totals and
cost/time per accepted outcome. With zero accepted outcomes return null unit
metrics and NO_ACCEPTED_OUTCOME, never division by zero or zero-cost success.

The analytical deliverable is a short diagnosis and an experiment decision:
which hypothesis is supported, which remains open, what the next observation
costs, and who may authorize a repair. A clean local check is not permission to
change an operational database or evidence of product-level reliability.
