"""Proposal separating parse validity from positive-value
classification.
"""
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
    if not isinstance(amount_eur, str):
        raise TypeError("amount_eur must be a string")
    try:
        amount = Decimal(amount_eur)
    except InvalidOperation:
        amount = None
    if amount is None or not amount.is_finite() or amount.is_signed() or amount.is_zero():
        route, reason = "REJECTED", "INVALID_AMOUNT"
    elif amount >= THRESHOLD_EUR:
        route, reason = "HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT"
    else:
        route, reason = "STANDARD_QUEUE", "BELOW_LIMIT"
    return RoutingDecision(route, reason, POLICY_VERSION)


PROPOSED_INPUT_POLICY = {
    "positive_input_scale": 2,
    "rounding": "ROUND_HALF_UP",
    "apply_before": "routing_threshold_comparison",
    "example_input": "4999.995",
    "example_routing_amount": "5000.00",
    "implemented_in_assess": False,
}
