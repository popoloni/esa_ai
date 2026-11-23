# B4 decision record

## Expect

Contract: OPS-B4/v2 (docs/contract.md, docs/policy_catalog.json, AGENTS.md read; no conflicts or missing mappings found).
Outcome: `inspect_ledger`, `diagnose`, `recovery_plan` in incident.py distinguish a wrong *selected state* from a source regression, read-only, and propose (not perform) restoration.

Acceptance example: expected ledger = active BR-001/v2 + anchor "anchor"; wrong ledger = fresh, active BR-001/v1, no anchor, but both contain request "old" with the same decision_id.
`diagnose(wrong, expected, expected_policy="BR-001/v2", anchor_key="anchor")` -> `WRONG_LEDGER` with exactly {STATE_PATH_MISMATCH, ACTIVE_POLICY_MISMATCH, ANCHOR_MISSING}, both files byte-identical afterwards. Diagnosing expected vs expected -> `EXPECTED_LEDGER_SELECTED`, no issues. `recovery_plan` has `restore_configuration_to` = resolved expected path, `automatic_merge` False, `production_authorized` False.

Open owner question: how to handle records created while the wrong ledger was selected (reconciliation). Not decided; plan reports `PENDING_OWNER_DECISION`.

## Delegate

Edited only incident.py (replaced three NotImplementedError stubs; kept `cost_summary` import from operations as the G4 accounting) and this file. ledger.py, routing.py, operations.py, docs, tests, prior/, READER_ENTRY.json untouched.

## Observe

- Baseline `python -m unittest tests.test_b4`: 7 tests, 6 errors (NotImplementedError) - missing behavior reproduced; only the cost test passed.
- After implementation, same command: 7 tests, OK.
- `sha256sum` of ledger.py, routing.py, operations.py matches READER_ENTRY.json (checked prefixes 8e87f6bd…, e8fdab89…, f0162261… after the change; ledger.py and routing.py also matched in full before editing).
- An earlier attempt to write incident.py via a shell heredoc was blocked by the tool's safety check; no file changed; I rewrote it with the file-edit tool. (Command count so far about 6 of 40.)

Corrections explained: `request_id` in inspect output is the ledger column `request_key` (tests need that name). Paths are resolved so the same ledger via different spellings is not a false mismatch. Missing paths raise FileNotFoundError before any sqlite connect, since sqlite would otherwise create them.

Limits / uncertainty: `inspect_ledger` does not run the full record-integrity checks of PolicyStore (it avoids PolicyStore because that would write/initialize). It does not validate the expected ledger against expected_policy/anchor; it only reports its observed values. If the expected ledger is itself wrong, the result is still driven by the three listed checks. Only the supplied tests were run; no WAL-mode ledgers, corrupted files or non-ledger SQLite files were tried (WRONG_DATABASE / UNSUPPORTED_SCHEMA paths are untested). Human acceptance remains PENDING.

## Decide

- Proposal 1, diagnose by state difference rather than source change: ACCEPT (matches contract; tests pass).
- Proposal 2, recovery_plan as proposal-only with `restore_configuration_to`: ACCEPT, with the field only naming a binding; restoration is the operator's separate action.
- Proposal 3, merging or reconciling wrong-ledger records: ASK the owner. Not implemented, not authorized.
Handoff scope: selected state = wrong ledger path/digest; source version unchanged (dependency hashes match); observed policy BR-001/v1 vs expected v2; preserved evidence = both ledgers; restoration = proposed only; reconciliation = unresolved; next authorized check = operator's protected acceptance and continuation.
(The three proposals are not enumerated in the supplied documents; I interpreted them as above. Please correct if they differ.)
