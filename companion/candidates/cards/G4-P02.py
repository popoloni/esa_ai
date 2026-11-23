return {
    "attempts": len(attempts),
    "accepted_outcomes": accepted,
    "total_cost_eur": str(money),
    "total_minutes": str(minutes),
    "cost_per_accepted_eur": (
        None if accepted == 0 else str(money / len(attempts))),
    "minutes_per_accepted": (
        None if accepted == 0 else str(minutes / accepted)),
    "status": (
        "NO_ACCEPTED_OUTCOME" if accepted == 0 else "ACCOUNTED")}
