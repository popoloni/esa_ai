try:
    cursor = connection.execute(
        "INSERT INTO bookings_v2 (payload) VALUES (?)",
                                (json.dumps(payload),))
    identifier = cursor.lastrowid
    connection.commit()
finally:
    connection.close()
return Outcome(201, "confirmed", identifier)
