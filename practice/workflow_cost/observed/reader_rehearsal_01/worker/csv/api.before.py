"""Existing JSON presentation; add CSV after the same selection boundary."""
from selection import selected_orders, public_order

def orders_response(rows, actor, format="json", status=None):
    selected = selected_orders(rows, actor, status)
    public = [public_order(row) for row in selected]
    if format == "json":
        return {"content_type": "application/json", "body": public}
    if format == "csv":
        raise NotImplementedError("CSV presentation requested but not implemented")
    raise ValueError("unsupported format")
