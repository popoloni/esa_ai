"""A recommendation routing service. This module never authorizes fund movement."""
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

THRESHOLD_EUR = Decimal("5000.00")
POLICY_VERSION = "BR-001/v1"
# B1-API/v2 (B1-OD-02): explicit ASCII monetary-text grammar, max 32 chars.
MAX_LENGTH = 32
_GRAMMAR = re.compile(r"[+-]?[0-9]+(?:\.[0-9]{1,2})?")

@dataclass(frozen=True)
class RoutingDecision:
    route: str
    reason: str
    policy_version: str

def _rejected() -> RoutingDecision:
    return RoutingDecision("REJECTED", "INVALID_AMOUNT", POLICY_VERSION)

def assess(amount_eur: str) -> RoutingDecision:
    """Choose a processing queue. Not a payment authorisation."""
    if not isinstance(amount_eur, str):
        raise TypeError("amount_eur must be a str")
    # Syntax gate first; fullmatch (not $) so a trailing newline is rejected.
    if len(amount_eur) > MAX_LENGTH or _GRAMMAR.fullmatch(amount_eur) is None:
        return _rejected()
    try:
        amount = Decimal(amount_eur)  # only conversion is guarded
    except InvalidOperation:
        return _rejected()
    # Finiteness first: ordered comparison of NaN/sNaN would raise.
    if not amount.is_finite() or amount <= 0:
        return _rejected()
    if amount < THRESHOLD_EUR:
        return RoutingDecision("STANDARD_QUEUE", "BELOW_LIMIT", POLICY_VERSION)
    return RoutingDecision("HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT", POLICY_VERSION)
