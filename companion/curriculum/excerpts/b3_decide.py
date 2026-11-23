def _decide(self, key, payload, version, parent):
    valid_key(key)
    fingerprint = digest(canonical_payload(payload))
    if version is not None:
        # Explicit caller intent is separate from the
        # ambient policy.
        self._policy(version)
    existing = self.conn.execute(
        "SELECT * FROM decisions WHERE request_key=?", (key,)
    ).fetchone()
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
    policy = self._policy(version or self.active_policy())
    identity = _insert(
        self.conn, key, canonical(payload), canonical(policy),
        canonical(outcome(payload, policy)), parent
    )
    self.conn.execute("""
            INSERT INTO audit_events (
                event_type, request_key, evidence_json
            ) VALUES ('DECISION_RECORDED',?,?)
        """, (key, canonical({
        "decision_id": identity, "parent_key": parent})))
    return {"status": "CREATED", "record": self.replay(key)}
