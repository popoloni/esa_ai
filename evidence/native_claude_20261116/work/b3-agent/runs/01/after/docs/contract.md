# B3: preserve decisions while policy evolves

Owner: fictional Treasury policy owner and ledger maintainer. Approved teaching
contract HISTORY-API/v1 and MIGRATION/v1, 2025-05-21. New schema version 2 is
separate from API and business policy versions. Policy catalogue: BR-001/v1 has
threshold 5000.00; BR-001/v2 has threshold 3000.00. Both retain finite-positive
classification and never authorize payment. The retained router keeps BR-001/v1 numeric behavior. Independent entry supplies B1-API/v1; continuation carries the explicit B1-API/v2 implementation. HISTORY inputs are a compatible subset of both.

Use PolicyStore(path,catalog). decide(request_id,payload,policy_version=None)
creates a record once. Payload contains amount_eur and beneficiary_id; the ledger
API accepts finite ASCII decimal text with at most 12 integer digits and 2
fractional digits, optional minus, and a bounded ASCII beneficiary identifier.
Canonical numeric spelling is used for retry identity while original payload field values remain stored in canonical JSON. Identity excludes the ambient active policy.

After activate(v2), retrying the same request ID and canonical payload returns
the stored v1 decision without a new decision or audit row. Changed payload or
an explicit incompatible policy under an old ID raises IDEMPOTENCY_CONFLICT
without mutation. replay returns stored evidence; recompute uses the recorded
policy snapshot without creating a row; reevaluate(old_id,new_id,v2) requires a
new ID and records its parent. Activation persists across restart.

migrate_legacy(path,catalog,provenance) is explicit, transactional, and retains
the legacy table unchanged. It requires the protected synthetic source ID,
row digest, historical payload, policy and outcome. Missing provenance or an
ambiguous historical rule is a stop condition, never a default to current policy.
Records and audit history cannot be edited or deleted through the provided store.
These local checks do not grant production migration or financial authority.

The storage grammar is `-?[0-9]{1,12}(?:\.[0-9]{1,2})?` with fullmatch.
It accepts leading zeros within the 12-integer-digit limit but not a leading plus;
canonical identity removes redundant zeros and fixes two fractional digits.
B1-API/v2 separately permits a plus sign and a total length of 32 characters.
A value allowed by that router can therefore be rejected by the ledger boundary.
Both use ASCII [0-9] and fullmatch: final newlines and Unicode digits are refused.
