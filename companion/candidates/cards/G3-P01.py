def quote_refund(paid_eur, *, hours_before):
    """Proposed quote for a new refund interface; no payment
    is made.
    """
    from decimal import Decimal
    fraction = Decimal("1") if hours_before >= 24 else Decimal(
        "0.5")
    return Decimal(str(paid_eur)) * fraction
