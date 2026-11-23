# Contribution B: reservation CLI

## Scope and design

Implemented only `reservation_cli.py` under `INTEGRATION-G3/v1`. The CLI uses `argparse` for the required `inspect`, `--database`, and positive-integer `--reservation-id` arguments. It calls `reservation_report.build_report(path, reservation_id)` once and serializes the returned report as one JSON object on stdout. Found reports return 0; absent reports return 3. Argument errors use argparse's exit 2. SQLite errors and filesystem `OSError` failures print a concise storage error on stderr and return 2 before printing any report. Other unexpected errors propagate. Importing the module does not invoke `main`; the script entry exits with its result.

The CLI does not read tables, initialize storage, interpret reservation history or state, or manufacture report data. No protected component, documentation, or tests were edited. The report module remains the supplied unimplemented contributor A stub.

## Acceptance example and actual component observations

The acceptance example exercised by the protected component test is:

```python
main(['inspect', '--database', 'chosen.sqlite', '--reservation-id', '41'])
```

With the test's explicit fake report provider returning:

```json
{"found": true, "reservation": {"sentinel": "public report"}, "current": {"state": "cancelled", "version": 2}}
```

The test observed exit status 0, stdout that parses to exactly this report, empty stderr, and one provider call with integer reservation ID 41. The sentinel payload belongs only to the protected test; it is not embedded in the implementation and does not demonstrate a real storage read.

Both component runs used the supplied recorder and this selection:

```text
python3 -m unittest discover -s tests -p test_integration_b.py -v
```

- Capture 007: baseline exit 1; all three tests errored on the deliberate `NotImplementedError("Contribution B")` stub. That failure remains in the record.
- Capture 009: exit 0; all three tests passed in 0.003 seconds after implementation.
- The passing selection covers the found example above; an absent fake report with exit 3 and exact JSON; a fake `sqlite3.OperationalError('no database')` with exit 2, empty stdout and nonempty stderr; and identifiers `0`, `-1`, and `abc` with exit 2 and empty stdout.

Missing arguments, filesystem errors, and actual script subprocess behavior are implemented but are not separate assertions in this component selection. No additional test selection or combined acceptance was run by this contributor.

## Integration assumptions and operator handoff

The operator must combine this actual completed CLI with contributor A's actual completed `reservation_report.py` and the retained `booking.py`. The report provider must satisfy the exact contract: a JSON-serializable object with a boolean `found`, the historical six-field record or null, and current state/version or null. Storage exceptions are allowed to reach this CLI for translation into the specified error response. Historical confirmation and current cancellation remain separate meanings; this CLI makes no claim that the provider's separate reads are a concurrent snapshot.

Component success uses an explicit fake provider and establishes only contributor B behavior. It does not establish combined import or real database behavior. Independent acceptance of confirmed, cancelled, absent, and missing-storage cases in the combined extracted package belongs to the operator. No commit or merge was performed.
