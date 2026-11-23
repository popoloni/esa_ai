"""Proposal using binary floating-point parsing."""
from dataclasses import dataclass
import math
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
        amount = float(amount_eur)
    except ValueError:
        return RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)
    if not math.isfinite(amount) or amount <= 0:
        return RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)
    if amount < 5000.0:
        return RoutingDecision("STANDARD_QUEUE", "BELOW_LIMIT", POLICY_VERSION)
    return RoutingDecision("HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT", POLICY_VERSION)
