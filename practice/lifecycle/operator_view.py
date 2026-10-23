"""Versioned operator projection for the same Treasury routing increment.

The router, or a recorded PolicyStore decision, chooses the route. This module
explains that result and refuses unknown policy or contradictory input. It does
not grant payment authority or claim that operators benefited from the wording.
"""
from decimal import Decimal, InvalidOperation

from treasury.explanation_alpha import build_explanation

SCHEMA = "treasury-operator-explanation/v2"
POLICIES = {"BR-001/v1": "5000.00", "BR-001/v2": "3000.00"}
PAYMENT_NOTICE = "Payment approval is separate from this queue recommendation."


def amount_text(value):
    """Retain meaningful precision; do not round a boundary input up or down."""
    text = format(value, ",f")
    whole, dot, fraction = text.partition(".")
    return whole + "." + fraction.ljust(2, "0")


def present(amount_eur, decision, policy):
    """Project a supplied decision using its recorded, explicit policy snapshot."""
    version = decision.get("policy_version")
    if (version not in POLICIES or policy.get("version") != version
            or policy.get("threshold_eur") != POLICIES[version]
            or policy.get("algorithm") != "TREASURY_THRESHOLD_V1"):
        raise ValueError("UNKNOWN_OR_MISMATCHED_POLICY")
    if (decision.get("payment_authorized") is not False
            or decision.get("notice") != "ROUTING_ONLY_NOT_PAYMENT_APPROVAL"):
        raise ValueError("PAYMENT_AUTHORITY_MISMATCH")
    try:
        amount = Decimal(amount_eur)
        valid = amount.is_finite() and amount > 0
    except (InvalidOperation, TypeError, ValueError):
        amount, valid = None, False
    route, reason = decision.get("route"), decision.get("reason_code")
    threshold = Decimal(policy["threshold_eur"])
    if route == "REJECTED" and reason == "INVALID_AMOUNT" and not valid:
        recommendation = "Stop and correct the amount."
        explanation = "The amount must be a finite positive number."
        next_action = "Enter a valid amount and request a new routing recommendation."
    elif route == "STANDARD_QUEUE" and reason == "BELOW_LIMIT" and valid and amount < threshold:
        recommendation = "Send to the standard queue."
        explanation = "EUR " + amount_text(amount) + " is below the EUR " + amount_text(threshold) + " routing threshold."
        next_action = "Continue with the standard queue's review procedure."
    elif route == "HUMAN_REVIEW" and reason == "AT_OR_ABOVE_LIMIT" and valid and amount >= threshold:
        recommendation = "Send for human review."
        comparison = "equals" if amount == threshold else "is above"
        explanation = "EUR " + amount_text(amount) + " " + comparison + " the EUR " + amount_text(threshold) + " routing threshold."
        next_action = "Ask the designated reviewer to assess the request before further processing."
    else:
        # Checking the explanation is not permission to replace the supplied
        # route with a newly calculated one. A contradiction stops presentation.
        raise ValueError("DECISION_EXPLANATION_MISMATCH")
    return {
        "schema": SCHEMA,
        "recommendation": recommendation,
        "reason": explanation,
        "policy": version + " (routing threshold EUR " + amount_text(threshold) + ")",
        "next_action": next_action,
        "payment_notice": PAYMENT_NOTICE,
    }


def explain_for_operator(amount_eur):
    """Use the actual CP08 implementation and its original v1 routing contract."""
    decision = build_explanation(amount_eur)
    policy = {"version": "BR-001/v1", "threshold_eur": "5000.00", "algorithm": "TREASURY_THRESHOLD_V1"}
    return present(amount_eur, decision, policy)


def explain_record(record):
    """A historical explanation uses the saved decision and saved policy."""
    return present(record["payload"]["amount_eur"], record["decision"], record["policy"])


def plain_text(view):
    return "\n".join((view["recommendation"], view["reason"], "Policy: " + view["policy"],
                       "Next: " + view["next_action"], view["payment_notice"]))
