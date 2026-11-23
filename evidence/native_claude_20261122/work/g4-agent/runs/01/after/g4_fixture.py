"""Authored corruption fixture for the explicitly supported G3 representations.

OPS-G4/v3 names three representations. When `advance G4` records the owner
mapping G4-OD-01 for a lineage, `docs/G4-SCHEMA-MAP.json` next to this file adds
that lineage's own layout. This helper creates test data. It is not product
diagnosis or a recovery command.
"""
from pathlib import Path
import json
import sqlite3
REFERENCE=("id","asset_id","member_id","starts_at","ends_at","request_key","request_hash","state","version")
RECORDED=("reservation_id","trusted_member_id","asset_id","starts_at","ends_at","idempotency_key","payload_fingerprint","state","version")
NATIVE=("id","trusted_member_id","asset_id","starts_at","ends_at","idempotency_key","fingerprint","state","version")
INSERT_ROLES=("asset_id","member_id","starts_at","ends_at","request_key","request_hash")
NAMED_ROLES={REFERENCE:dict(zip(("id",*REFERENCE[1:]),REFERENCE)),
             RECORDED:{"id":"reservation_id","member_id":"trusted_member_id","asset_id":"asset_id",
                       "starts_at":"starts_at","ends_at":"ends_at","request_key":"idempotency_key",
                       "request_hash":"payload_fingerprint","state":"state","version":"version"},
             NATIVE:{"id":"id","member_id":"trusted_member_id","asset_id":"asset_id",
                     "starts_at":"starts_at","ends_at":"ends_at","request_key":"idempotency_key",
                     "request_hash":"fingerprint","state":"state","version":"version"}}


def owner_mapping():
    """Return the lineage mapping recorded by G4-OD-01, or None."""
    path=Path(__file__).resolve().parent/"docs"/"G4-SCHEMA-MAP.json"
    if not path.is_file():
        return None
    data=json.loads(path.read_text(encoding="utf-8"))
    return data["table"],tuple(data["signature"]),dict(data["roles"])


def create_competing_representations(path, *, progressive):
    """Create two recognized *current* layouts, not an old historical table.

    OPS-G4/v3 requires the observer to refuse this ambiguity. With an owner
    mapping, the "native" variant pairs the reference table with the lineage's
    own mapped layout. This deliberately invalid teaching database is never a
    migration or recovery operation.
    """
    if progressive not in ("recorded", "native"):
        raise ValueError("Select the recorded or native progressive layout")
    table, signature, roles = "reservations_v2", (RECORDED if progressive == "recorded" else NATIVE), None
    mapped = owner_mapping()
    if progressive == "native" and mapped and mapped[0] != "reservations":
        table, signature, roles = mapped
    integers = {"id", "reservation_id", "version"} if roles is None else {roles["id"], roles["version"]}
    with sqlite3.connect(path) as con:
        for name, columns in (("reservations", REFERENCE), (table, signature)):
            definitions = [column + (" INTEGER" if column in integers else " TEXT") for column in columns]
            con.execute('CREATE TABLE "' + name + '" (' + ", ".join(definitions) + ")")
        con.execute("PRAGMA user_version=3")


def insert_overlap(path, *, asset="A", member="m2", start="2025-05-16T09:30:00Z", end="2025-05-16T10:30:00Z", key="bad"):
    layouts=[("reservations",REFERENCE,NAMED_ROLES[REFERENCE]),("reservations_v2",RECORDED,NAMED_ROLES[RECORDED]),
             ("reservations_v2",NATIVE,NAMED_ROLES[NATIVE])]
    mapped=owner_mapping()
    if mapped:
        layouts.append(mapped)
    with sqlite3.connect(path) as con:
        choices=[]
        for table,signature,roles in layouts:
            found=tuple(row[1] for row in con.execute('PRAGMA table_info("'+table+'")'))
            if found==signature:choices.append((table,signature,roles))
        if len(choices)!=1:raise ValueError("Fixture requires exactly one documented current representation")
        table,signature,roles=choices[0]
        values=dict(asset_id=asset,member_id=member,starts_at=start,ends_at=end,request_key=key,
                    request_hash="author-corruption-fixture")
        columns=[roles[role] for role in INSERT_ROLES]
        parameters=[values[role] for role in INSERT_ROLES]
        if mapped and (table,signature)==mapped[:2]:
            # A mapped layout may not declare defaults; state the active row explicitly.
            columns+= [roles["state"],roles["version"]];parameters+=["active",1]
        sql=('INSERT INTO "'+table+'"('+",".join('"'+c+'"' for c in columns)+") VALUES("
             +",".join("?"*len(columns))+")")
        con.execute(sql,parameters)
