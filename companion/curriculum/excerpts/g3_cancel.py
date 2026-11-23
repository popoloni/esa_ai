def cancel(
    path, reservation_id, *, trusted_member_id, expected_version
):
    con = sqlite3.connect(path, isolation_level=None, timeout=10)
    try:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("""
            SELECT member_id, state, version FROM reservations
            WHERE id=?
        """, (reservation_id,)).fetchone()
        if row is None:
            result = {"status":404, "code":"not-found"}
        elif row[0] != trusted_member_id:
            result = {"status":403, "code":"not-owner"}
        elif row[2] != expected_version:
            result = {"status":409, "code":"stale-version"}
        elif row[1] == "cancelled":
            result = {"status":200, "code":"already-cancelled",
                      "version":row[2]}
        else:
            con.execute("""
                UPDATE reservations SET state='cancelled',
                version=version+1 WHERE id=?
            """, (reservation_id,))
            result = {"status":200, "code":"cancelled",
                      "version":row[2]+1}
        con.execute("COMMIT")
        return result
    except BaseException:
        if con.in_transaction:
            con.execute("ROLLBACK")
        raise
    finally:
        con.close()
