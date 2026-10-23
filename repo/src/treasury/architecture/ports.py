"""Design B. A routing port and injected presenter for a different test seam.
No payment authorization, threshold change, persistence or network access.
"""
from dataclasses import dataclass
from typing import Callable
from treasury.routing import RoutingDecision, assess

NOTICE = "ROUTING_ONLY_NOT_PAYMENT_APPROVAL"

@dataclass(frozen=True)
class RoutingPort:
    decide: Callable[[str], RoutingDecision]

@dataclass(frozen=True)
class ExplanationPresenter:
    routing: RoutingPort

    def explain(self, amount_eur: str) -> dict:
        decision = self.routing.decide(amount_eur)
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


def explain(amount_eur: str) -> dict:
    return ExplanationPresenter(RoutingPort(assess)).explain(amount_eur)
