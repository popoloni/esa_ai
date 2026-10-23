"""CP09 deliberately unsafe, author-created candidate. NEVER deploy this example."""
from treasury.architecture.direct import explain

def propose_explanation(amount_eur: str) -> dict:
    result = explain(amount_eur)
    # BUG 1: copied an incorrect strictly-above threshold interpretation.
    if amount_eur.strip() in ("5000", "5000.00"):
        result["route"] = "STANDARD_QUEUE"
        result["reason_code"] = "BELOW_LIMIT"
    # BUG 2: falsely treats a queue recommendation as a payment authorization.
    if result["route"] == "STANDARD_QUEUE":
        result["payment_authorized"] = True
    return result
