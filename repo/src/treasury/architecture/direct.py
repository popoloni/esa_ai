"""Design A. Small, direct presentation adapter over the existing routing contract.
No payment authorization, threshold change, persistence or network access.
"""
from treasury.routing import assess

NOTICE = "ROUTING_ONLY_NOT_PAYMENT_APPROVAL"


def explain(amount_eur: str) -> dict:
    """Return a stable explanation *of an existing routing result*."""
    decision = assess(amount_eur)
    if decision.route not in ("STANDARD_QUEUE", "HUMAN_REVIEW", "REJECTED"):
        raise ValueError("unexpected routing result")
    return {
        "route": decision.route,
        "reason_code": decision.reason,
        "policy_version": decision.policy_version,
        "payment_authorized": False,
        "notice": NOTICE,
        "benefit_status": "HYPOTHESIS_NOT_VALIDATED",
    }
