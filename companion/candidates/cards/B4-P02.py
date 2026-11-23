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
