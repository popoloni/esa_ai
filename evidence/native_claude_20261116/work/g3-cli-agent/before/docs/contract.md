# G3: cancellation without breaking existing callers

Owner: fictional workshop coordinator. Approved teaching contract (fictional case date) RES-002/v1,
2025-05-19. Schema version becomes 3; business reservation identity is unchanged.
Migrate existing G2 rows to state active and version 1 without changing IDs or
public fields. Existing get_reservation retains its six-field shape, including
for a cancelled reservation: it is a historical record lookup.

Add reservation_status(path,id), returning {state,version} or None. Add
cancel(path, id, *, trusted_member_id, expected_version). The caller supplies
a trusted member ID and an integer expected version. Only the owning member may
cancel. Missing ID returns 404/not-found; wrong owner returns 403/not-owner;
stale version returns 409/stale-version. These outcomes make no changes.
A valid active cancellation returns 200/cancelled and increments version once.
A repetition with the current cancelled version returns 200/already-cancelled
without another increment. The old version is stale even if the row is cancelled.
Check and transition are atomic. The API assumes valid typed boundary arguments;
a network authentication boundary is not implemented by this local module.

Cancelled intervals no longer block a new reservation. Replaying the original
reserve request still returns its original operation identity and confirmation;
reservation_status supplies current state. Replaying an operation must not revive
it. Requests to refund, physically delete history or permit staff overrides
require new owner decisions and are outside this contract.
