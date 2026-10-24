# ADR-0001 — First durable reservation slice

**Status:** Teaching choice, not an approved production architecture.

**Context.** The accepted learning objective is to observe an atomic write boundary and independent concurrency test in a small local environment. The product's scale and actual member uptake have not been measured.

**Options.** In-memory state demonstrates rule semantics but loses reservations on restart and does not establish concurrency safety. A single transactional SQLite database provides a durable test boundary with little machinery. Distributed services would add coordination and operational risks without a demonstrated requirement.

**Decision.** Use SQLite `BEGIN IMMEDIATE` before conflict read and insert, in one transaction. The transaction serializes writers for the local database. Use a UNIQUE `(member_id, request_key)` index, canonical UTC-second text timestamps, and a single overlapping-interval predicate.

**Consequences.** We can demonstrate the desired invariant on one file-backed store, but this does not establish multi-instance scalability, network identity, end-to-end latency, production backups or independent database replicas. Revisit after an approved throughput requirement, second deployment region or a new capacity model.

**Falsifying evidence.** Two successful overlapping confirmations after concurrent calls; replay creating a second row; inability to restore correct state after a crash; observed load outside the measured envelope.
