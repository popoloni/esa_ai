"""Existing owner-controlled selection. Do not broaden access for CSV."""
def selected_orders(rows, actor, status=None):
    return [row for row in rows
            if row["owner"] == actor and (status is None or row["status"] == status)]

def public_order(row):
    return {field: row[field] for field in
            ("order_id", "status", "customer", "amount_eur", "note")}
