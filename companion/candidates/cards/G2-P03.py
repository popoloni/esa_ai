request_hash = hashlib.sha256(json.dumps([asset,start,end],
    separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
con.execute("INSERT INTO reservations VALUES(?,?,?,?,?,?,?)",
            (identifier, asset, member, start, end, key,
                request_hash))
if con.in_transaction: con.execute("ROLLBACK")
raise
