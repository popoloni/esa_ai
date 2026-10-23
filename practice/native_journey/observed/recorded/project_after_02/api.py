"""Existing JSON presentation; add CSV after the same selection boundary."""
from selection import selected_orders, public_order

def orders_response(rows, actor, format="json", status=None):
    selected = selected_orders(rows, actor, status)
    public = [public_order(row) for row in selected]
    if format == "json":
        return {"content_type": "application/json", "body": public}
    if format == "csv":
        return {"content_type": "text/csv; charset=utf-8", "body": csv_formatter(selected)}
    if format == "other":
        raise ValueError("unsupported format")

def csv_formatter(rows):
    import csv
    import io
    output = io.StringIO()
    csv.writer(output).writerow(['order_id', 'status', 'customer', 'amount_eur', 'note'])
    for row in rows:
        csv.writer(output).writerow([row['order_id'], row['status'], row['customer'], row['amount_eur'], row['note']])
    return output.getvalue()
    raise ValueError("unsupported format")
