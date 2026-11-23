def diagnose(
    selected_path, expected_path, *, expected_policy, anchor_key
):
    selected, expected = (
        inspect_ledger(selected_path), inspect_ledger(
            expected_path))
    issues = []
    if selected["path"] != expected["path"]:
        issues.append("STATE_PATH_MISMATCH")
    if selected["active_policy"] != expected_policy:
        issues.append("ACTIVE_POLICY_MISMATCH")
    if anchor_key not in {
        r["request_id"] for r in selected["decisions"]
    }:
        issues.append("ANCHOR_MISSING")
    return {
        "status": (
            "WRONG_LEDGER" if issues else
                "EXPECTED_LEDGER_SELECTED"),
        "issues": issues, "selected": selected, "expected":
            expected,
        "restoration": "NOT_PERFORMED",
        "reconciliation": "PENDING_OWNER_DECISION"}

def recovery_plan(diagnosis):
    return {
        "restore_configuration_to": diagnosis["expected"]["path"],
        "preserve_ledgers": [
            diagnosis["selected"]["path"],
            diagnosis["expected"]["path"]],
        "verification": [
            "historical replay",
            "current-policy decision on disposable copy",
            "restart and state binding"],
        "automatic_merge": False,
        "reconciliation": "PENDING_OWNER_DECISION",
        "production_authorized": False}
