# Contribution A: read-only reservation report

Role: report. Contract: INTEGRATION-G3/v1. Owned files: `reservation_report.py`, this note.

## Acceptance example (derived before implementation)

Initialized storage; member `m-1` reserves asset `A`, 2025-05-16T09:00:00Z to 10:00:00Z, key `k-1`.

- `build_report(path, id)` returns exactly
  `{"found": True, "reservation": {reservation_id, trusted_member_id, asset_id, starts_at, ends_at, idempotency_key}, "current": {"state": "active", "version": 1}}`.
- After `booking.cancel(..., expected_version=1)` the same call returns the same `reservation`
  (the original record is unchanged) with `current == {"state": "cancelled", "version": 2}`.
- An absent ID (e.g. 999) in initialized storage returns exactly
  `{"found": False, "reservation": None, "current": None}`.
- Missing storage raises `sqlite3.OperationalError` and the file is not created.
- Database bytes are identical before and after every call.

## Design

`build_report` only calls the public `booking.get_reservation` and `booking.reservation_status`
(both open storage read-only). No SQL, no `init_db`, no writes, no exception handling:
all errors propagate. The two reads are separate and not one concurrent snapshot.
If the record exists but status is then missing (not expected, as deletion is not supported),
a `RuntimeError` is raised rather than inventing a state.

## Verification and limits

Component test: `tests/test_integration_a.py`, using the real booking API (no fake dependencies for A).
Results are recorded in the run report, not claimed here. This does not establish
combined behaviour with Contribution B or the extracted package; the operator owns that.
