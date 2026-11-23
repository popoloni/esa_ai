# Contribution B: reservation CLI

Owner: CLI role. Files: `reservation_cli.py`, `CONTRIBUTION_B.md`. Contract: INTEGRATION-G3/v1.

## Acceptance example (derived before editing)

| Invocation | stdout | stderr | exit |
|---|---|---|---|
| `inspect --database db.sqlite --reservation-id 41`, report returns `found: true` | one JSON object, the report unchanged | empty | 0 |
| `inspect ... --reservation-id 99`, report returns `found: false` | `{"found": false, "reservation": null, "current": null}` | empty | 3 |
| report raises `sqlite3.Error` / `OSError` (e.g. missing database) | empty | one concise `error: ...` line | 2 |
| `--reservation-id 0`, `-1`, `abc`, or a missing argument | empty | argparse usage error | 2 |

## Design
- `main(argv=None)` parses with argparse and calls `reservation_report.build_report(database, id)` through the module attribute. It does no SQL, initialisation or report semantics, and embeds no data.
- Only `sqlite3.Error` and `OSError` are treated as storage errors. Any other exception propagates.
- Importing does not run the CLI. The `__main__` guard exits with `main`'s status.

## Verification status
- Component test `tests/test_integration_b.py` uses a fake report provider (`build_report` patched with `unittest.mock`) and no real storage. Its result is recorded in the run report, not here.
- This is not a combined check. Real behaviour with Contribution A on a confirmed record, after cancellation, for an absent ID and for missing storage is for the operator to verify in the extracted package.

## Integration assumptions
- `reservation_report.build_report(path, reservation_id)` returns a dict with a boolean `found`, per the contract, and raises storage errors unchanged.
- The database path is passed as a string as given.
