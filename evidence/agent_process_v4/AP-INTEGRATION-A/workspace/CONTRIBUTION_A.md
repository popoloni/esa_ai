# Contribution A: read-only reservation report

## Scope and design

Implemented only `reservation_report.py` under INTEGRATION-G3/v1.
`build_report(path, reservation_id)` calls the retained public
`booking.get_reservation` operation first. If the historical record is absent,
it returns the exact three-field absent report. If present, it obtains
`booking.reservation_status` and returns the unchanged historical record
alongside current state and version.

There is no initialization, SQL access, booking mutation, exception interception,
or replacement of the original confirmation. Unexpected public-operation errors
propagate to the caller. The implementation adds no booking rules.

## Acceptance example

The protected component test creates a reservation with this historical record,
where `r` is the reservation ID returned by the real `booking.reserve`:

```python
{
    "reservation_id": r,
    "trusted_member_id": "m-1",
    "asset_id": "A",
    "starts_at": "2025-05-16T09:00:00Z",
    "ends_at": "2025-05-16T10:00:00Z",
    "idempotency_key": "k-1",
}
```

The report has `found=True`, that exact six-field record as `reservation`,
and `current={"state": "active", "version": 1}`. After owner cancellation
with expected version 1, the same report operation retains the historical
record and returns `current={"state": "cancelled", "version": 2}`.
The test compares database bytes before and after each report call.

In initialized storage, absent ID 999 produces exactly
`{"found": False, "reservation": None, "current": None}`, with database
bytes unchanged. Missing storage raises `sqlite3.OperationalError` and
does not create a database file.

## Actual component-test observations

Only the assigned component selection was run:

```text
python3 -B -m unittest discover -s tests -p test_integration_a.py -v
```

- Recorder command 003, before implementation: exit 1; 3 tests ran;
  all 3 raised the stub's `NotImplementedError("Contribution A")`.
- Recorder command 005, after implementation: exit 0; 3 tests ran; all passed
  in 0.005 seconds.
- Passing cases were `test_history_and_current_state_remain_distinct`,
  `test_absent_is_an_observation`, and
  `test_missing_storage_is_not_created`.
- These component tests use the real retained booking API. No fake dependency
  was introduced.

## Integration assumptions and remaining verification

The operator must combine this file with contributor B's completed CLI and
the retained `booking.py` using the agreed public imports and interface.
The other contribution remained an intentionally unimplemented stub here.

The historical record and current status are separate public reads, not an
atomic concurrent snapshot. The retained G3 API supports cancellation without
deleting history; this implementation assumes that agreed storage lifecycle.
Absence is the observation returned by the historical read. Public API errors
are not converted into absence.

Combined imports, CLI JSON output, exit statuses, stderr behavior, and execution
from an extracted package have not been verified by this contribution. The
operator owns those integration checks against the actual completed modules.
No commit or merge was performed.
