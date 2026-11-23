if existing is not None:
    record = self._record(existing)
    if (
        record["request_fingerprint"] != fingerprint
        or record["parent_key"] != parent
        or (version is not None
            and version != record["policy_version"])
    ):
        raise HistoryError("IDEMPOTENCY_CONFLICT")
    return {"status": "REPLAYED", "record": record}
