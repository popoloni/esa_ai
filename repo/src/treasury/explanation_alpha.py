"""CP08 deliberately faulty starter. Do not deploy or claim payment approval."""
from treasury.architecture.direct import explain

def build_explanation(amount_eur: str) -> dict:
    decision=explain(amount_eur)
    return {
       'status_label': 'APPROVED' if decision['route']=='STANDARD_QUEUE' else decision['route'],
       'route': decision['route'],
       'reason_code': decision['reason_code'],
       'policy_version': 'BR-001/v2',  # invented by the faulty starter
       'payment_authorized': decision['payment_authorized'],
       'notice': decision['notice'],
       'benefit_status': 'VALUE_PROVEN',  # not observed
    }
