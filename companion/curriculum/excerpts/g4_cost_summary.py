def cost_summary(attempts, accepted):
    if type(accepted) is not int or accepted < 0:
        raise ValueError("accepted must be a nonnegative count")
    money = Decimal("0")
    minutes = Decimal("0")
    for a in attempts:
        try:
            cost = Decimal(str(a["cost_eur"]))
            duration = Decimal(str(a["minutes"]))
        except InvalidOperation as error:
            raise ValueError(
                "cost and time must be decimal numbers"
            ) from error
        if (not cost.is_finite() or not duration.is_finite()
                or cost < 0 or duration < 0):
            raise ValueError(
                "cost and time must be finite and nonnegative"
            )
        money += cost
        minutes += duration
    return {
        "attempts": len(attempts),
        "accepted_outcomes": accepted,
        "total_cost_eur": str(money),
        "total_minutes": str(minutes),
        "cost_per_accepted_eur": (
            None if accepted == 0 else str(money / accepted)),
        "minutes_per_accepted": (
            None if accepted == 0 else str(minutes / accepted)),
        "status": (
            "NO_ACCEPTED_OUTCOME" if accepted == 0 else
                "ACCOUNTED")}
