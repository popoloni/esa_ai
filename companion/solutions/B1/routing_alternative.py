"""Choose a queue with a default rejection and one final
decision return.
"""
from dataclasses import dataclass
import decimal

THRESHOLD_EUR = decimal.Decimal("5000.00")
POLICY_VERSION = "BR-001/v1"


@dataclass(frozen=True)
class RoutingDecision:
    route: str
    reason: str
    policy_version: str


def assess(amount_eur: str) -> RoutingDecision:
    if not isinstance(amount_eur, str):
        raise TypeError("amount_eur must be a string")
    try:
        amount = decimal.Decimal(amount_eur)
    except decimal.InvalidOperation:
        amount = None
    route, reason = "REJECTED", "INVALID_AMOUNT"
    if amount is not None and amount.is_finite() and amount > 0:
        if amount >= THRESHOLD_EUR:
            route, reason = "HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT"
        else:
            route, reason = "STANDARD_QUEUE", "BELOW_LIMIT"
    return RoutingDecision(route, reason, POLICY_VERSION)
