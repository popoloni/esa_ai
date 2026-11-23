# G3 decision record

## Expect

Implement RES-002/v1 from the supplied contract on the retained G2 candidate. Keep reservation IDs, all six historical public fields, operation identity and the original reserve confirmation. Schema version 3 adds active/version 1 for existing records. Status is a separate current-state read. Cancellation is one atomic owner/version-checked operation; cancelled intervals become available without deleting or reviving history.

Acceptance examples recorded before implementation:
- Retained G2 reservation 41 migrates to schema 3, active/version 1, with identical historical fields and fingerprint. Reinitialization preserves its state.
- The explicitly supplied legacy G2 implementation also migrates losslessly; it is a second supported source, not a replacement for the retained implementation.
- Missing ID returns 404/not-found; wrong owner returns 403/not-owner; stale version returns 409/stale-version. Every rejection leaves data unchanged.
- Owner/version 1 cancels an active row with 200/cancelled and version 2. Current version 2 repeats as 200/already-cancelled at version 2. Version 1 remains stale afterward.
- Two concurrent requests with expected version 1 yield one cancellation and one stale-version result, with one version increment.
- A new identity can reserve the released interval. Replaying the original identity returns its original 200/confirmed reservation ID, never reactivates it, and changed payload under that identity still conflicts.
- Historical get_reservation retains exactly its six fields; reservation_status returns only state/version or None. Existing request validation, half-open intervals, migrations and fail-closed unknown-schema handling remain in place.

Uncertainties and implementation decisions: the supplied tests establish a mapping-shaped cancellation result with status/code and a version on successful cancellation. The contract assumes trusted, correctly typed caller inputs; this module does not add an authentication boundary or staff permissions. Both G2 schema mappings are explicit in the retained code and supplied dependency. Preserve the supplied legacy source table and its indexes during conversion, and recognize that exact retained source on subsequent initialization. No consequential owner mapping is presently missing. Independent acceptance remains the operator responsibility.

## Delegate

Bounded change: booking.py and this dossier only. Protect docs, supplied tests, legacy_booking.py, prior snapshots and metadata. Use only the required recorder for task reads, edits and checks; no network or external services. At most 40 recorded commands, 45 seconds each. A reasoning-only parallel review was attempted but unavailable because the agent thread limit was reached; no helper executed.

## Observe

- Recorded 001: workspace file inventory; no files changed.
- Recorded 002: read AGENTS.md, contract, retained booking.py, supplied legacy dependency, G3 tests and initial dossier. Confirmed status and cancel are unimplemented; retained schema version is 2 and differs from the supplied legacy fixture.
- Recorded 003: this pre-edit acceptance record. Baseline reproduction and development receipts follow below.


- Recorded 004: baseline supplied test run, `python3 -B -m unittest discover -s tests -v`, FAILED with 7 errors. Every failure was the alternate G2 schema rejection: version 2 current table is missing; owner mapping required. No test files changed.
- Recorded 005: separate retained-candidate reproduction FAILED deliberately after observing schema version 2 and NotImplementedError from both status and cancel. This confirmed the retained candidate had its own missing behavior rather than treating the fixture as the implementation.
- Recorded 006: implemented booking.py. Retained reservations_v2 is upgraded in place; explicitly supplied G2 reservations are validated and copied to that canonical table with the source preserved. All paths reach user_version 3 and active/version 1 defaults atomically. Added read-only status, owner/version-checked cancellation under BEGIN IMMEDIATE, and active-only conflict checks. Historical reads, original operation identity, fingerprint checks and confirmation replay remain intact.
- Recorded 007: supplied development suite PASSED all 7 tests.
- Recorded 008: PASSED 11 migration/lifecycle cases using the actual supplied prior/booking.py snapshot, legacy_booking.py, and fresh initialization. Covered retained G2 with empty/columnar/public/JSON origins, alternate G2 with empty/columnar/JSON origins, and fresh G3 with all four origins. Verified IDs 1 or 41, exact historical fields, unchanged source definitions/rows, schema 3, initial state/version, mutation-free rejection outcomes, cancellation, replacement booking, replay identity, changed-payload conflict, repeated cancellation and reinitialization.
- Recorded 009: PASSED four concurrency scenarios. Two expected-version-1 cancellations yielded exactly one 200/cancelled and one 409/stale-version, ending at cancelled/version 2. Competing claims of the released interval yielded one 201 and one 409. Concurrent same-key reserve yielded one creation and one replay with the same ID. A simultaneous reserve/cancel run observed interval-conflict before cancellation committed, then succeeded on retry; this is a valid serial order.
- Recorded 010: PASSED 10 fail-closed schema/data-mapping cases with identical database bytes and logical dumps after rejection (unknown version/table/trigger, column/index drift, alternate-fixture fingerprint or timestamp corruption, unknown archive, and an extra G3 index). Also passed eight unchanged request-validation rejections, adjacency/overlap checks, the inclusive 24-hour limit, and historical/status read-only missing-database behavior.
- Recorded 011: completed this receipt and handoff record. Only booking.py and DOSSIER.md were edited. No operator correction was used; 11 of the 40-command budget were used. All recorded commands completed below the 45-second limit.

Development conclusion: the implemented behavior satisfies the exercised approved G3 examples on both actual supplied G2 implementations. These are development checks, not independent acceptance or integration. No extra API for refunds, erasure or staff overrides was added. No consequential mapping remains unresolved for the supplied schemas.

Limits: cancellation assumes the contractually trusted member identity and correctly typed expected version; network authentication is outside this module. Unknown schema/data mappings fail with an owner-mapping requirement. Concurrent behavior was checked with local SQLite threads and separate connections, not an external deployment or exhaustive scheduling exploration. Source archives are preserved by this module, not protected by an operating-system access boundary.

## Decide

ACCEPT: implement the approved owner-only/version-checked cancellation and explicit migrations described above.
REJECT under present authority: refunds, physical deletion of reservation history, and staff cancellation overrides (the three out-of-contract proposals). ASK for a new owner decision if any is requested; do not infer permission from this implementation task.
Handoff will report actual development results and remaining limits, without claiming independent acceptance, human participation or unverified model identity.
