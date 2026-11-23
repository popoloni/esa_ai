prior = con.execute("""
            SELECT id, request_key FROM reservations
            WHERE member_id = ? AND request_key = ?
        """, (trusted_member_id, idempotency_key)).fetchone()
if prior is not None:
    con.execute('COMMIT')
    if prior[1] == idempotency_key:
        return Outcome(
            200, 'confirmed', prior[0], replayed=True
        )
    return Outcome(409, 'idempotency-key-reused')
