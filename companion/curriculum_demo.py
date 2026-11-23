#!/usr/bin/env python3
"""Execute a retained candidate against explicit offline continuation fixtures.

Output is author/lab evidence, not a human pilot, observed model run, financial
operation, or production incident. Monetary/time inputs are labelled scenarios.
"""
from pathlib import Path
from dataclasses import asdict
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(folder, name, data):
    path = folder / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return path


def request(key="original", member="member-14", asset="lathe-2"):
    return dict(trusted_member_id=member, asset_id=asset,
                starts_at="2025-05-16T13:00:00Z", ends_at="2025-05-16T14:00:00Z",
                idempotency_key=key)


def g2(folder):
    import booking, legacy_g1
    db = folder / "reservations.sqlite"
    legacy_g1.init_db(db)
    original = legacy_g1.reserve(db, **request())
    before = legacy_g1.get_reservation(db, original.reservation_id)
    with sqlite3.connect(db) as con:
        legacy_columns = [row[1] for row in con.execute('PRAGMA table_info(reservations)')]
        legacy_rows = con.execute('SELECT * FROM reservations ORDER BY id').fetchall()
    booking.init_db(db)
    replay = booking.reserve(db, **request())
    conflict = booking.reserve(db, **{**request(), "ends_at":"2025-05-16T15:00:00Z"})
    adjacent = booking.reserve(db, **{**request("adjacent", "member-22"),
                                    "starts_at":"2025-05-16T14:00:00Z", "ends_at":"2025-05-16T15:00:00Z"})
    after = booking.get_reservation(db, original.reservation_id)
    assert after == before and replay.replayed and replay.reservation_id == original.reservation_id
    assert conflict.status == 409 and adjacent.status == 201
    with sqlite3.connect(db) as con:
        historical_tables = []
        for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            quoted = '"' + name.replace('"', '""') + '"'
            columns = [row[1] for row in con.execute('PRAGMA table_info(' + quoted + ')')]
            if columns == legacy_columns:
                rows = con.execute('SELECT * FROM ' + quoted + ' ORDER BY id').fetchall()
                if rows == legacy_rows:
                    historical_tables.append(name)
    assert historical_tables, 'Original legacy columns and rows were not preserved in a historical table'
    preserved = len(legacy_rows)
    data = {"initial_public_record":before,"after_migration":after,
            "same_identity_replay":asdict(replay),"changed_payload":asdict(conflict),
            "adjacent_new_request":asdict(adjacent),"legacy_rows_preserved":preserved,
            "historical_tables":historical_tables,
            "history_check":"Exact original column signature and rows; no reference-specific archive table name."}
    write(folder, "continuation.json", data)
    return data


def g3(folder):
    import booking, legacy_booking
    db = folder / "reservations.sqlite"
    legacy_booking.init_db(db)
    original = legacy_booking.reserve(db, **request())
    old_record = legacy_booking.get_reservation(db, original.reservation_id)
    booking.init_db(db)
    wrong_owner = booking.cancel(db, original.reservation_id, trusted_member_id="other-member", expected_version=1)
    cancelled = booking.cancel(db, original.reservation_id, trusted_member_id="member-14", expected_version=1)
    stale = booking.cancel(db, original.reservation_id, trusted_member_id="member-14", expected_version=1)
    current = booking.reservation_status(db, original.reservation_id)
    replay = booking.reserve(db, **request())
    replacement = booking.reserve(db, **request("replacement", "member-22"))
    assert wrong_owner["status"] == 403 and cancelled["version"] == 2 and stale["status"] == 409
    assert booking.get_reservation(db, original.reservation_id) == old_record
    assert replay.replayed and current == {"state":"cancelled", "version":2} and replacement.status == 201
    data = {"old_public_record":old_record,"wrong_owner":wrong_owner,"cancellation":cancelled,
            "stale_version":stale,"current_state":current,"original_operation_replay":asdict(replay),
            "replacement":asdict(replacement)}
    write(folder, "continuation.json", data)
    return data


def g4(folder):
    import booking, operations
    db = folder / "incident_fixture.sqlite"
    booking.init_db(db)
    booking.reserve(db, **request())
    clean = operations.diagnose(db)
    # Deliberate author fixture corruption, explicitly outside the public API.
    from g4_fixture import insert_overlap
    insert_overlap(db, asset="lathe-2", member="fixture-member",
                   start="2025-05-16T13:30:00Z", end="2025-05-16T14:30:00Z",
                   key="fixture-overlap")
    before = sha(db)
    diagnosis = operations.diagnose(db)
    assert diagnosis["diagnosis"] == "ACTIVE_OVERLAP" and sha(db) == before
    attempts = [{"id":"diagnosis-1","status":"rejected","cost_eur":"3.40","minutes":"12"},
                {"id":"diagnosis-2","status":"rejected","cost_eur":"0.60","minutes":"7"},
                {"id":"accepted-diagnosis","status":"accepted","cost_eur":"1.50","minutes":"18"}]
    cost = operations.cost_summary(attempts, 1)
    write(folder, "diagnosis.json", {"origin":"CONSTRUCTED_CORRUPTION_FIXTURE", "clean_control":clean,"observation":diagnosis,"repair_performed":False})
    write(folder, "cost_report.json", {"origin":"ILLUSTRATIVE_COST_INPUTS_NOT_MEASURED_PRODUCTIVITY","attempts":attempts,"accepted_outcomes":1,"summary":cost})
    return {"diagnosis":diagnosis["diagnosis"],"evidence_unchanged":sha(db)==before,
            "repair_authorized":False,"cost_scenario":cost,"human_acceptance":"PENDING"}


def b2(folder):
    import intake
    calls = []
    def provider(key, amount):
        calls.append({"request_id":key,"amount_eur":amount})
        if len(calls) == 1:
            raise intake.ProviderUnavailable("constructed one-call outage")
        return {"request_id":key,"classification":"REVIEW" if key=="item-2" else "MATCH"}
    items = [{"request_id":"item-invalid","amount_eur":"-0.01"},
             {"request_id":"item-1","amount_eur":"2400.00"},
             {"request_id":"item-2","amount_eur":"5000.00"},
             {"request_id":"item-3","amount_eur":"29.99"}]
    result = intake.evaluate_batch(items, provider, max_attempts=2, max_calls=3)
    assert result["calls"] == 3 and result["records"][-1]["status"] == "DEFERRED"
    assert not result["payment_authorized"]
    write(folder, "classification.json", {"origin":"DETERMINISTIC_LOCAL_PROVIDER_FIXTURE","requests":items,"observed_calls":calls,"result":result})
    return result


def b3(folder):
    import ledger
    catalog = json.loads((ROOT/"curriculum/policy_catalog.json").read_text())
    db = folder / "ledger.sqlite"
    payload = {"amount_eur":"4000.0", "beneficiary_id":"supplier_41"}
    store = ledger.PolicyStore(db, catalog)
    try:
        old = store.decide("case-original", payload)
        activation = store.activate("BR-001/v2")
        def counts():
            return {t:store.conn.execute("SELECT COUNT(*) FROM "+t).fetchone()[0] for t in ("decisions","audit_events")}
        before = counts()
        retry = store.decide("case-original", {**payload,"amount_eur":"4000.00"})
        after = counts()
        assert retry["record"] == old["record"] and before == after
        try:
            store.decide("case-original", {**payload,"amount_eur":"4100.00"})
        except ledger.HistoryError as exc:
            conflict = exc.code
        else:
            raise AssertionError("changed payload was not refused")
        assert conflict == "IDEMPOTENCY_CONFLICT" and counts() == before
        recomputed = store.recompute("case-original")
        new = store.reevaluate("case-original", "case-new-evaluation", "BR-001/v2")
        assert new["record"]["parent_key"] == "case-original"
        assert old["record"]["decision"]["route"] == "STANDARD_QUEUE"
        assert new["record"]["decision"]["route"] == "HUMAN_REVIEW"
    finally:
        store.close()
    store = ledger.PolicyStore(db, catalog)
    try:
        restart = {"active_policy":store.active_policy(),"old_decision_id":store.replay("case-original")["decision_id"]}
    finally:
        store.close()
    data = {"created":old,"activation":activation,"retry":retry,"counts_before_retry":before,
            "counts_after_retry":after,"payload_conflict":conflict,"recompute":recomputed,"reevaluation":new,
            "restart":restart,"schema_version":2,"api_contract":"HISTORY-API/v1"}
    write(folder, "history.json", data)
    return {"retry_status":retry["status"],"retry_rows_unchanged":before==after,
            "original_policy":"BR-001/v1","active_policy":restart["active_policy"],
            "new_parent":new["record"]["parent_key"],"payment_authorized":False}


def b4(folder):
    import ledger, incident
    catalog = json.loads((ROOT/"curriculum/policy_catalog.json").read_text())
    expected, wrong = folder/"expected.sqlite", folder/"wrong.sqlite"
    payload = {"amount_eur":"4000.00","beneficiary_id":"supplier_41"}
    for path in (expected, wrong):
        store = ledger.PolicyStore(path, catalog)
        try:
            store.decide("old", payload)
            if path == expected:
                store.decide("anchor", {**payload,"amount_eur":"12.00"})
                store.activate("BR-001/v2")
        finally:
            store.close()
    before = {str(p):sha(p) for p in (expected, wrong)}
    config = write(folder,"selected_state.json",{"ledger_path":str(wrong)})
    diagnosis = incident.diagnose(wrong, expected, expected_policy="BR-001/v2", anchor_key="anchor")
    plan = incident.recovery_plan(diagnosis)
    assert diagnosis["status"] == "WRONG_LEDGER" and not plan["automatic_merge"]
    configuration_before = json.loads(config.read_text())
    # Authorized teaching fixture restoration: only this local JSON binding changes.
    write(folder,"selected_state.json",{"ledger_path":plan["restore_configuration_to"]})
    positive = incident.diagnose(expected, expected, expected_policy="BR-001/v2", anchor_key="anchor")
    disposable = folder/"verification_copy.sqlite"
    shutil.copy2(expected, disposable)
    store = ledger.PolicyStore(disposable, catalog)
    try:
        replay = store.replay("old")
        current = store.decide("new-probe", payload)
    finally:
        store.close()
    store = ledger.PolicyStore(disposable, catalog)
    try:
        restart = store.replay("new-probe")["decision_id"] == current["record"]["decision_id"]
    finally:
        store.close()
    after = {str(p):sha(p) for p in (expected, wrong)}
    assert before == after and positive["status"] == "EXPECTED_LEDGER_SELECTED"
    assert replay["policy_version"] == "BR-001/v1" and current["record"]["policy_version"] == "BR-001/v2" and restart
    attempts = [{"id":"failed-diagnosis","cost_eur":"0.45","minutes":"4"},
                {"id":"diagnosis-and-review","cost_eur":"1.35","minutes":"19"},
                {"id":"fixture-restoration-check","cost_eur":"0.70","minutes":"11"}]
    cost = incident.cost_summary(attempts, 1)
    write(folder,"diagnosis.json",{"origin":"CONSTRUCTED_WRONG_LEDGER_FIXTURE","ledger_source_sha256":sha(Path(ledger.__file__)),"observation":diagnosis,"preserved_before":before,"preserved_after":after})
    write(folder,"recovery_plan.json",plan)
    write(folder,"restoration.json",{"origin":"LOCAL_CONFIGURATION_FIXTURE_ONLY","configuration_before":configuration_before,"configuration_after":json.loads(config.read_text()),"positive_control":positive,"historical_replay":replay,"current_policy_probe_on_copy":current,"restart_identity_match":restart,"original_ledgers_unchanged":before==after,"reconciliation":"PENDING_OWNER_DECISION"})
    write(folder,"cost_report.json",{"origin":"ILLUSTRATIVE_COST_INPUTS_NOT_MEASURED_PRODUCTIVITY","attempts":attempts,"accepted_outcomes":1,"summary":cost})
    return {"diagnosis":diagnosis["status"],"local_configuration_fixture_restored":True,
            "original_ledgers_unchanged":before==after,"reconciliation":"PENDING_OWNER_DECISION",
            "production_authorized":False,"cost_scenario":cost}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mission", choices=("G2","G3","G4","B2","B3","B4"))
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    candidate, output = args.candidate.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(candidate))
    result = globals()[args.mission.lower()](output)
    report = {"schema":"esa-curriculum-demonstration/v1","mission":args.mission,
              "recorded_at_utc":datetime.now(timezone.utc).isoformat(),"command":[sys.executable,*sys.argv],
              "origin":"EXECUTED_OFFLINE_TEACHING_FIXTURE","observed_human_pilot":False,
              "observed_model_run":False,"result":result}
    write(output,"DEMONSTRATION.json",report)
    print(json.dumps(report,indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
