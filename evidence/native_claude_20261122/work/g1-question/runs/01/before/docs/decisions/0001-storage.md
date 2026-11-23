# ADR G1/001 — minimal local storage

Decision: use a local SQLite file. Keep the schema private behind `reserve` and
`get_reservation`. Store enough data to return the six public fields after the
writer has exited. The normal reference uses one table with an integer identifier
and five text columns; the alternative uses a different table with a JSON payload.
Both are valid G1 designs and pass the same public checks.

Commit before returning `201/confirmed`. Bind request data as parameters. A
storage exception must remain visible. A request fingerprint, an idempotency
constraint and an overlap index are deferred until their behavior is introduced
in G2. No current test or continuation step reads internal columns.

The historical RES-001/v1 ten-case suite counts the original `reservations` table.
It is preserved unchanged in `historical_tests/` for provenance and compatibility
checks; it does not gate this slice. `--select all` uses a separately named API
adaptation and reports the full-contract scope explicitly.
