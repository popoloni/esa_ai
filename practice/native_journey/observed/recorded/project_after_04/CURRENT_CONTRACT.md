# CSV-001/v1: add one presentation

The existing orders API selects rows for a supplied actor and optional status.
This local exercise starts after authentication; actor establishment and HTTP
transport are outside its scope. CSV must use exactly the same authorized,
filtered rows and order as the JSON path. Do not change selection.py.

Preserve the existing JSON result and input data. Add `format="csv"` returning
content_type `text/csv; charset=utf-8` and a CSV string in body. Columns, in order:
order_id, status, customer, amount_eur, note. The output has a header even when
there are no rows. A standard CSV parser must recover each selected field,
including commas, double quotes, embedded newlines and Unicode. Unsupported
formats raise ValueError. Serialization must not alter or persist source rows.

Fictional owner decision CSV-CONSUMER-01: the target is a machine CSV importer,
not a spreadsheet. Preserve field values literally, including formula-like
strings. Do not silently prefix apostrophes. Spreadsheet viewing needs a
separately approved consumer format and checks; the CSV label alone gives no
assurance about spreadsheet interpretation. There are no production records.

Allowed implementation scope: api.py and an optional new presenter.py. Keep
selection, demo, fixtures and contract unchanged. A direct formatter or a small
presenter is valid if behavior meets this contract. Avoid new external packages.

Before editing, identify the row-selection dependency and state the constraints.
Keep the first failure, diff, independent checks and a compact fresh-session
handoff. The canonical worked solution is one choice, not a required syntax.
