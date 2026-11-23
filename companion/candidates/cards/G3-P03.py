con.execute("""
                UPDATE reservations SET state='cancelled',
                version=version+1 WHERE id=?
            """, (reservation_id,))
if row[0] != trusted_member_id:
    result = {"status":403, "code":"not-owner"}
else:
    result = {"status":200, "code":"cancelled",
              "version":row[2]+1}
