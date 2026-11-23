try:
    amount = float(amount_eur)
except ValueError:
    return RoutingDecision("REJECTED", "INVALID_AMOUNT",
        POLICY_VERSION)
if not math.isfinite(amount) or amount <= 0:
    return RoutingDecision("REJECTED", "INVALID_AMOUNT",
        POLICY_VERSION)
if amount < 5000.0:
    return RoutingDecision("STANDARD_QUEUE", "BELOW_LIMIT",
        POLICY_VERSION)
return RoutingDecision("HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT",
    POLICY_VERSION)
