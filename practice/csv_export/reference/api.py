"""One valid direct formatter. Selection remains owned by the existing API."""
import csv
from io import StringIO
from selection import selected_orders, public_order

FIELDS = ("order_id", "status", "customer", "amount_eur", "note")

def orders_response(rows, actor, format="json", status=None):
    public = [public_order(row) for row in selected_orders(rows, actor, status)]
    if format == "json":
        return {"content_type": "application/json", "body": public}
    if format != "csv":
        raise ValueError("unsupported format")
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(public)
    return {"content_type": "text/csv; charset=utf-8", "body": stream.getvalue()}
