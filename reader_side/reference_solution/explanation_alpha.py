"""Reference CP08 local presentation increment. Not production code or payment authority."""
from treasury.architecture.direct import explain

_LABELS = {
    'STANDARD_QUEUE': 'RECOMMENDED_STANDARD_QUEUE',
    'HUMAN_REVIEW': 'RECOMMENDED_HUMAN_REVIEW',
    'REJECTED': 'REJECTED',
}

def build_explanation(amount_eur: str) -> dict:
    """Render an existing routing result; never authorize or change a decision."""
    decision = explain(amount_eur)
    return {
      'status_label': _LABELS[decision['route']],
      'route': decision['route'],
      'reason_code': decision['reason_code'],
      'policy_version': decision['policy_version'],
      'payment_authorized': False,
      'notice': decision['notice'],
      'benefit_status': decision['benefit_status'],
    }
