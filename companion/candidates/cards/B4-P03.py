selected, expected = (
    inspect_ledger(selected_path), inspect_ledger(expected_path))
return {
    "status": (
        "WRONG_LEDGER" if issues else "EXPECTED_LEDGER_SELECTED"),
    "issues": issues, "selected": selected, "expected": expected,
    "restoration": "NOT_PERFORMED",
    "reconciliation": "PENDING_OWNER_DECISION"}
