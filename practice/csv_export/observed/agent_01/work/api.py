"""Existing JSON presentation; add CSV after the same selection boundary."""
import csv
import io

from selection import selected_orders, public_order

def orders_response(rows, actor, format="json", status=None):
    selected = selected_orders(rows, actor, status)
    public = [public_order(row) for row in selected]
    if format == "json":
        return {"content_type": "application/json", "body": public}
    if format == "csv":
        output = io.StringIO(newline="")
        writer = csv.DictWriter(
            output,
            fieldnames=("order_id", "status", "customer", "amount_eur", "note"),
        )
        writer.writeheader()
        writer.writerows(public)
        return {"content_type": "text/csv; charset=utf-8", "body": output.getvalue()}
    raise ValueError("unsupported format")
