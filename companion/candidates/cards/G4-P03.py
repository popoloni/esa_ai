def _billable_attempts(attempts):
    return [a for a in attempts if a.get("status") != "FAILED"]
attempts = _billable_attempts(attempts)
