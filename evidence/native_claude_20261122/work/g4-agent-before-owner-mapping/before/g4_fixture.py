"""Authored corruption fixture for the three explicitly supported G3 representations (OPS-G4/v3).
This helper creates test data. It is not product diagnosis or a recovery command.
"""
import sqlite3
REFERENCE=("id","asset_id","member_id","starts_at","ends_at","request_key","request_hash","state","version")
RECORDED=("reservation_id","trusted_member_id","asset_id","starts_at","ends_at","idempotency_key","payload_fingerprint","state","version")
NATIVE=("id","trusted_member_id","asset_id","starts_at","ends_at","idempotency_key","fingerprint","state","version")
def create_competing_representations(path, *, progressive):
    """Create two recognized *current* layouts, not an old historical table.

    OPS-G4/v3 requires the observer to refuse this ambiguity. This deliberately
    invalid teaching database is never a migration or recovery operation.
    """
    if progressive not in ("recorded", "native"):
        raise ValueError("Select the recorded or native progressive layout")
    signature = RECORDED if progressive == "recorded" else NATIVE
    with sqlite3.connect(path) as con:
        for table, columns in (("reservations", REFERENCE), ("reservations_v2", signature)):
            definitions = [name + (" INTEGER" if name in ("id", "reservation_id", "version") else " TEXT")
                           for name in columns]
            con.execute("CREATE TABLE " + table + " (" + ", ".join(definitions) + ")")
        con.execute("PRAGMA user_version=3")

def insert_overlap(path, *, asset="A", member="m2", start="2025-05-16T09:30:00Z", end="2025-05-16T10:30:00Z", key="bad"):
    with sqlite3.connect(path) as con:
        choices=[]
        for table,signature in (("reservations",REFERENCE),("reservations_v2",RECORDED),("reservations_v2",NATIVE)):
            found=tuple(row[1] for row in con.execute("PRAGMA table_info("+table+")"))
            if found==signature:choices.append((table,signature))
        if len(choices)!=1:raise ValueError("Fixture requires exactly one documented current representation")
        table,signature=choices[0]
        if signature==REFERENCE:
            sql="INSERT INTO reservations(asset_id,member_id,starts_at,ends_at,request_key,request_hash) VALUES(?,?,?,?,?,?)"
        elif signature==RECORDED:
            sql="INSERT INTO reservations_v2(asset_id,trusted_member_id,starts_at,ends_at,idempotency_key,payload_fingerprint) VALUES(?,?,?,?,?,?)"
        else:
            sql="INSERT INTO reservations_v2(asset_id,trusted_member_id,starts_at,ends_at,idempotency_key,fingerprint) VALUES(?,?,?,?,?,?)"
        con.execute(sql,(asset,member,start,end,key,"author-corruption-fixture"))
