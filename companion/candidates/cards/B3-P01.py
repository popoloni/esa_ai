if any(not isinstance(row.get(field), str) for field in (
    "payload_json", "policy_json", "decision_json")):
    raise HistoryError("HISTORY_AMBIGUOUS")
if not isinstance(policy, dict) or policy.get("version") not in \
    catalog or policy != catalog[policy["version"]]:
    raise HistoryError("HISTORY_AMBIGUOUS")
