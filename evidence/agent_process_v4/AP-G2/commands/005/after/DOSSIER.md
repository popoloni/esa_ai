# G2 decision record

## Expect

The public API remains init_db, reserve and get_reservation with unchanged Outcome fields and the G1 read-only lookup behavior. G2 adds exact UTC-second timestamp validation, nonempty string identifiers of at most 128 characters, positive intervals of at most 24 hours, half-open overlap exclusion per asset, member-scoped idempotent replay, payload fingerprints, and one atomic write transaction for the replay/conflict decision and insertion.

Acceptance examples derived before coding:

1. A new valid [09:00,10:00) request confirms with 201, a durable ID, and the original public values.
2. The identical member/key and payload returns 200/confirmed, the original ID and replayed=True, with exactly one reservation retained. A changed asset, start or end returns 409/idempotency-key-reused without mutation.
3. Another member/key on the same overlapping asset returns 409/interval-conflict. [10:00,11:00) and the same time on another asset succeed. Another member may independently reuse a request key.
4. Empty, non-string or over-128-character identifiers yield 422/invalid-identifier; noncanonical or impossible UTC timestamps yield 422/invalid-timestamp; zero, reversed or over-24-hour durations yield 422/invalid-interval. Exactly 24 hours is valid. Rejection creates no reservation.
5. Two local SQLite writers contending for the same slot produce one confirmation and one conflict. Concurrent identical requests produce one 201 and one 200 for the same ID.
6. Lookup returns only the six established public fields, returns None for an absent ID in valid storage, and raises without creating a file when storage is missing, including paths containing URI metacharacters.

Open requirements: prompt_01 explicitly prohibits migration, while docs/contract.md labels G2-OD-01 as authorization for two legacy migrations and the supplied diagnostic includes migration cases. The operator has been notified; migration remains outside the implementation boundary pending an explicit correction. The contract requires distinct 422 outcomes but supplies no literal code strings; the three descriptive code strings above are the recorded implementation choice. No separate three-proposal document is supplied; decisions below identify the three concrete scope proposals considered here.

## Delegate

Only booking.py and DOSSIER.md may change. Preserve tests, docs, dependencies, prior snapshots and READER_ENTRY.json. Do not inspect parent/project/solution/study files or use network or external services. All task commands use the AP-G2 recorder. Independent acceptance belongs to the AI recording operator.

## Observe

AP-G2/001 inventories the initially relevant files. AP-G2/002 reads AGENTS.md, every supplied document under docs and the initial dossier. AP-G2/003 reads the retained booking.py and supplied test module. AP-G2/004 inventories workspace filenames. The retained implementation performs an unconditional reservation INSERT and has no validation, replay, overlap exclusion or fingerprint.

Development checks and implementation observations follow below after execution; no check result is yet claimed.

## Decide

ACCEPT: bounded G2 validation and half-open exclusion, subject to the derived examples.

ACCEPT: member-scoped replay with a stored payload fingerprint and an atomic SQLite write transaction, preserving public lookup fields.

ASK: legacy schema conversion and version-2 migration. The current direct task instruction prohibits it despite the supplied decision document and diagnostic. Do not implement migration until the operator resolves the scope conflict. No later mission capability is authorized.
