def _unique_requests(requests):
    rows = list(requests)
    ids = [row["request_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate request_id in this batch")
    return rows
requests = _unique_requests(requests)
