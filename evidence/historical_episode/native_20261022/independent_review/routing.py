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

def assess(amount_eur: str) -> RoutingDecision:
    """Choose a processing queue. Not a payment authorisation."""
    try:
        amount = Decimal(amount_eur)
        if not Decimal.is_finite(amount):
            return RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)
        if amount <= Decimal("0.00"):
            return RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)
        if amount < THRESHOLD_EUR:
            return RoutingDecision("STANDARD_QUEUE", "BELOW_LIMIT", POLICY_VERSION)
        return RoutingDecision("HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT", POLICY_VERSION)
    except InvalidOperation:
        return RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)
