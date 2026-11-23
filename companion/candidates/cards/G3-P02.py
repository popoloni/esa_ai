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
