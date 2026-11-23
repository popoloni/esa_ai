# G1-OD-01: complete the public read contract

Owner: fictional workshop coordinator. Status: approved teaching decision.
Fictional case decision date: 2025-05-14. Applies to G1/I01 after the initial-question step.
This is a supplied teaching response, not evidence that a human owner approved a learner's question.

For an initialized existing database, a lookup of an identifier that does not
exist returns `None`. For an identifier that exists, return a new mapping with
the six public fields specified in G1/I01. No mutation is allowed during a read.

A database path that does not exist is a different condition: storage has not
been initialized or its path is wrong. Raise `sqlite3.OperationalError` and do
not create a file. Do not turn it into `None`, which would incorrectly assert
that a query completed against known storage. Open the SQLite URI in `mode=ro`;
construct the URI with `Path.resolve().as_uri()` so spaces, `?`, and `#` in paths
are encoded as path data. Unexpected storage failures propagate.

The lookup case is now specified before the checks are delivered. Record whether
your question identified this gap. An omitted question is useful learning data,
not grounds to fabricate earlier recognition after reading this answer.
