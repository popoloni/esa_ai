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

## Decide

ACCEPT: implement the approved owner-only/version-checked cancellation and explicit migrations described above.
REJECT under present authority: refunds, physical deletion of reservation history, and staff cancellation overrides (the three out-of-contract proposals). ASK for a new owner decision if any is requested; do not infer permission from this implementation task.
Handoff will report actual development results and remaining limits, without claiming independent acceptance, human participation or unverified model identity.
