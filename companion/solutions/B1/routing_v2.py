"""Implement B1-API/v2 without changing BR-001/v1 numeric
policy.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re

THRESHOLD_EUR = Decimal("5000.00")
POLICY_VERSION = "BR-001/v1"
API_VERSION = "B1-API/v2"
MONEY_TEXT = re.compile(r"[+-]?[0-9]+(?:\.[0-9]{1,2})?", re.ASCII)

@dataclass(frozen=True)
class RoutingDecision:
    route: str
    reason: str
    policy_version: str

def assess(amount_eur: str) -> RoutingDecision:
    """Classify approved monetary text; keep caller and
    internal errors visible.
    """
    if not isinstance(amount_eur, str):
        raise TypeError("amount_eur must be a string")
    if len(amount_eur) > 32 or MONEY_TEXT.fullmatch(amount_eur) is None:
        return RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)
    try:
        amount = Decimal(amount_eur)
    except InvalidOperation:
        return RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)
    if not amount.is_finite() or amount <= 0:
        return RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)
    if amount < THRESHOLD_EUR:
        return RoutingDecision("STANDARD_QUEUE", "BELOW_LIMIT", POLICY_VERSION)
    return RoutingDecision("HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT", POLICY_VERSION)
