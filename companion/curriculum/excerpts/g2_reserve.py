def reserve(db_path: str | Path, *, trusted_member_id: str,
            asset_id: str, starts_at: str, ends_at: str,
            idempotency_key: str) -> Outcome:
    """Reserve [start,end) for an authenticated caller;
    never trusts payload identity.
    """
    if not all(
        isinstance(x, str) and x.strip() and len(x) <= 128
        for x in (trusted_member_id, asset_id, idempotency_key)
    ):
        return Outcome(422, 'invalid-identifier')
    try:
        start = _parse_utc_seconds(starts_at)
        end = _parse_utc_seconds(ends_at)
    except (ValueError, TypeError):
        return Outcome(422, 'invalid-timestamp')
    if not timedelta(0) < end - start <= timedelta(hours=24):
        return Outcome(422, 'invalid-interval')

    fingerprint = hashlib.sha256(json.dumps(
        [asset_id, starts_at, ends_at],
        separators=(',', ':'), ensure_ascii=True
    ).encode('utf-8')).hexdigest()
    con = sqlite3.connect(
        str(db_path), timeout=10, isolation_level=None
    )
    try:
        con.execute('PRAGMA busy_timeout=10000')
        # One transaction protects both check and insert.
        con.execute('BEGIN IMMEDIATE')
        prior = con.execute("""
            SELECT id, request_hash FROM reservations
            WHERE member_id = ? AND request_key = ?
        """, (trusted_member_id, idempotency_key)).fetchone()
        if prior is not None:
            con.execute('COMMIT')
            if prior[1] == fingerprint:
                return Outcome(
                    200, 'confirmed', prior[0], replayed=True
                )
            return Outcome(409, 'idempotency-key-reused')
        clash = con.execute("""
            SELECT 1 FROM reservations
            WHERE asset_id = ? AND starts_at < ? AND ends_at > ?
            LIMIT 1
        """, (asset_id, ends_at, starts_at)).fetchone()
        if clash is not None:
            con.execute('COMMIT')
            return Outcome(409, 'interval-conflict')
        cursor = con.execute("""
            INSERT INTO reservations (
                asset_id, member_id, starts_at, ends_at,
                request_key, request_hash
            ) VALUES (?,?,?,?,?,?)
        """, (asset_id, trusted_member_id, starts_at, ends_at,
              idempotency_key, fingerprint))
        reservation_id = cursor.lastrowid
        con.execute('COMMIT')
        return Outcome(201, 'confirmed', reservation_id)
    except Exception:
        if con.in_transaction:
            con.execute('ROLLBACK')
        raise
    finally:
        con.close()
