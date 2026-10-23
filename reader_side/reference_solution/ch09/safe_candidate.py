"""CP09 author reference: a bounded presenter, NOT a payment authorization."""
from treasury.architecture.direct import explain

def propose_explanation(amount_eur: str) -> dict:
    return explain(amount_eur)
