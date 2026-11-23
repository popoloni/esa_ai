# Contribution B — reservation CLI

Owner: CLI role. File: `reservation_cli.py`. Contract: INTEGRATION-G3/v1.

## Acceptance example (derived before editing)

Given a report provider returning for id 41
`{"found": true, "reservation": {...}, "current": {"state": "cancelled", "version": 2}}`:

    reservation_cli.py inspect --database chosen.sqlite --reservation-id 41

- calls `reservation_report.build_report("chosen.sqlite", 41)` (id as int);
- stdout: exactly one JSON object equal to the report, nothing else; stderr empty; exit 0.

Other cases: `found: false` report -> same printing, exit 3; `--reservation-id 0|-1|abc`,
missing/unknown arguments -> exit 2, stdout empty; `sqlite3.Error`/`OSError` from the
provider -> one concise line on stderr, stdout empty, exit 2.

## Design
- `main(argv=None)` returns the status (argparse usage errors are converted to the return value 2);
  `__main__` does `raise SystemExit(main())`; importing runs nothing.
- Calls `reservation_report.build_report` via module attribute at call time. No SQL, no storage
  initialisation, no report semantics, no embedded data.
- Only `sqlite3.Error` and `OSError` are treated as storage errors; other exceptions propagate.

## Component check
`test_integration_b.py` uses a fake (patched) `build_report`; the real report (A) and booking were
not exercised by it. It does not show combined behaviour.

## Integration assumptions for the operator
- A's `build_report(path, reservation_id)` returns a JSON-serialisable dict with a boolean `found`.
- A lets a missing database surface as `sqlite3.OperationalError` (booking's read-only open), not
  create the file. If A raises another type for missing storage (e.g. ValueError), the CLI will
  propagate a traceback rather than exit 2.
- Still to verify by the operator: the real CLI on a confirmed record, after cancellation, an absent
  ID and missing storage, in the extracted package.
