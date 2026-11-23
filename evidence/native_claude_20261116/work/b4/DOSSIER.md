# B4 decision record

## Expect

Contract OPS-B4/v2 (docs/contract.md, docs/policy_catalog.json). Outcome: `incident.py` implements
`inspect_ledger`, `diagnose`, `recovery_plan` (and re-exports G4 `cost_summary`) without writing to any ledger.

Acceptance example: selected `wrong.sqlite` (default policy v1, no `anchor`) vs expected `expected.sqlite`
(active BR-001/v2, anchor present) -> `status=WRONG_LEDGER`, issues
`STATE_PATH_MISMATCH, ACTIVE_POLICY_MISMATCH, ANCHOR_MISSING`, both files byte-identical afterwards, even though
decision `old` has the same `decision_id` in both. Selecting the expected ledger as both sides gives
`EXPECTED_LEDGER_SELECTED` with no issues. `recovery_plan` returns `restore_configuration_to` = resolved expected
path, `automatic_merge` False, `production_authorized` False.

Open owner question (not decided here): what to do with records created while the wrong ledger was selected
(reconciliation). The plan reports `PENDING_OWNER_DECISION`.

## Delegate

Only `incident.py` (implementation) and `DOSSIER.md` edited. Docs, tests, ledger.py, routing.py, operations.py,
prior/ and READER_ENTRY.json untouched. The stub raised `NotImplementedError` in all three functions (read from source;
I did not run a separate before-run).

Design choices and why:
- Read-only open via SQLite `mode=ro` URI; missing path raises `FileNotFoundError` before any connect (no creation).
- Application ID and `user_version` checked against `ledger.APPLICATION_ID` / `SCHEMA_VERSION`; mismatch raises `HistoryError`.
- File SHA-256 taken before and after observation; a change raises.
- `ANCHOR_MISSING` = anchor request key absent from the selected ledger's decisions.
- Equal decision IDs are reported in `shared_decision_ids` but `lineage_established` is always False.
- Plan also includes a compatibility alias `restore_state_binding_to`, and `next_authorized_check`.

## Observe

- `python -m unittest discover -s tests -p test_b4.py -v` -> Ran 7 tests, OK (all 7 pass, including the
  v2 consumer-field test). This is the only test file present.
- `sha256sum` of ledger.py, routing.py, operations.py equals the values in READER_ENTRY.json `dependency_sha256`.
  READER_ENTRY.json was only hashed, not edited.
- No corrections were needed after the first test run; there was one tool-side hiccup (a shell command was blocked by
  a safety check on the heredoc), so the file was written with the file-write tool instead. No failed test runs.
- `git status` run in the parent showed modified files under `../../companion/` that I did not touch; they are outside this workspace.

## Decide

- ACCEPT (locally, as a development result): read-only inspection, diagnosis, and the structured recovery proposal.
- ASK / not decided: reconciliation of records written to the wrong ledger, and any production recovery. Both need the owner.
- REJECT: any automatic merge or production authorization (the plan hard-codes both to False).
- Handoff scope: selected state = path of the ledger diagnosed; source version = unchanged ledger.py hash above;
  observed policy = selected ledger active policy; preserved evidence = both ledgers (digests in the diagnosis);
  restoration decision = proposal only; unresolved = reconciliation; next check = operator restart/state check.

Limits: human acceptance remains PENDING. Protected acceptance and continuation were not run by me. Tests are local fixtures;
no production incident, WAL/concurrent-writer behavior, or corrupted-ledger handling beyond the app-ID/version checks was tested.
Anchor check is key presence only (it does not compare anchor payload or decision ID). Paths are compared after `resolve()`.
