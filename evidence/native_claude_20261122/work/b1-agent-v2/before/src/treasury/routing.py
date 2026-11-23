"""A recommendation routing service. This module never authorizes fund movement."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

THRESHOLD_EUR = Decimal("5000.00")
POLICY_VERSION = "BR-001/v1"

@dataclass(frozen=True)
class RoutingDecision:
    route: str
    reason: str
    policy_version: str

_REJECTED = RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)


def assess(amount_eur: str) -> RoutingDecision:
    """Choose a processing queue. Not a payment authorisation."""
    if not isinstance(amount_eur, str):
        raise TypeError("amount_eur must be a str")
    try:
        amount = Decimal(amount_eur)
    except InvalidOperation:  # only conversion failure is an invalid amount
        return _REJECTED
    # Finiteness first: ordered comparison of NaN/sNaN would raise.
    if not amount.is_finite() or amount <= 0:
        return _REJECTED
    if amount < THRESHOLD_EUR:
        return RoutingDecision("STANDARD_QUEUE", "BELOW_LIMIT", POLICY_VERSION)
    return RoutingDecision("HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT", POLICY_VERSION)
