try:
    amount = Decimal(amount_eur)
except InvalidOperation:
    amount = None
if amount is None or not amount.is_finite() or amount.is_signed() \
    or amount.is_zero():
    route, reason = "REJECTED", "INVALID_AMOUNT"
elif amount >= THRESHOLD_EUR:
    route, reason = "HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT"
else:
    route, reason = "STANDARD_QUEUE", "BELOW_LIMIT"
return RoutingDecision(route, reason, POLICY_VERSION)
