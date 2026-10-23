"""Previous synthetic presentation artifact: core explanation without the CP08 label.

BR-001/v1 and the routing contract are unchanged. This is a local rollback
fixture, not evidence of a production release or a database migration.
"""
from treasury.architecture.direct import explain


def build_explanation(amount_eur: str) -> dict:
    return explain(amount_eur)
