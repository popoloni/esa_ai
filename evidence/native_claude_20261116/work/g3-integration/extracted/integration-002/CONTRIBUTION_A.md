# Contribution A: reservation report

## Acceptance example (derived before editing)
Storage initialised; member m-1 reserves asset A 2025-05-16T09:00Z–10:00Z, key k-1.
- `build_report(db, id)` -> found true, the six-field record, current `{state: active, version: 1}`.
- After `cancel(..., expected_version=1)` the record is unchanged and current is `{state: cancelled, version: 2}`.
- `build_report(db, 999)` in initialised storage -> `{found: false, reservation: null, current: null}`.
- Missing database file: `sqlite3.OperationalError` propagates; no file is created.

## Implementation
`reservation_report.py` calls only `booking.get_reservation` and `booking.reservation_status` (read-only, `mode=ro`). No SQL, no init, no mutation. The record is never altered by state. If a record exists but status is absent (not expected without deletion), `LookupError` is raised rather than guessing. The two reads are not one snapshot.

## Checks
Component check: `tests/test_integration_a.py`. Fake dependencies: none (real `booking` API on temp SQLite files). It does not show combined CLI behaviour.

## Integration assumptions
CLI (B) imports `reservation_report.build_report`, maps `found` to exit 0/3 and storage errors (e.g. `sqlite3.OperationalError`) to exit 2. The operator owns combination and extracted-package acceptance.
