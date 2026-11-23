from pathlib import Path
from tempfile import TemporaryDirectory
import json,sqlite3,unittest
import ledger
CATALOG={v:{"version":v,"threshold_eur":t,"algorithm":"TREASURY_THRESHOLD_V1"} for v,t in (("BR-001/v1","5000.00"),("BR-001/v2","3000.00"))}
PAYLOAD={"amount_eur":"4000.00","beneficiary_id":"supplier_41"}
class PersistentDecisions(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.db=Path(t.name)/"ledger.sqlite"
        self.store=ledger.PolicyStore(self.db,CATALOG);self.addCleanup(self.store.close)
    def counts(self):
        return tuple(self.store.conn.execute("SELECT COUNT(*) FROM "+table).fetchone()[0] for table in ("decisions","audit_events"))
    def test_retry_after_policy_change_returns_exact_old_decision(self):
        original=self.store.decide("original",PAYLOAD)["record"]
        self.store.activate("BR-001/v2");before=self.counts()
        replay=self.store.decide("original",PAYLOAD)
        self.assertEqual(replay["status"],"REPLAYED")
        self.assertEqual(replay["record"],original)
        self.assertEqual(self.counts(),before)
    def test_changed_payload_conflicts_without_new_rows(self):
        self.store.decide("original",PAYLOAD);before=self.counts()
        with self.assertRaises(ledger.HistoryError) as e:self.store.decide("original",{**PAYLOAD,"amount_eur":"4100.00"})
        self.assertEqual(e.exception.code,"IDEMPOTENCY_CONFLICT");self.assertEqual(self.counts(),before)
    def test_reevaluation_requires_new_identity_and_parent(self):
        old=self.store.decide("old",PAYLOAD)["record"]
        new=self.store.reevaluate("old","new","BR-001/v2")["record"]
        self.assertEqual((old["decision"]["route"],new["decision"]["route"]),("STANDARD_QUEUE","HUMAN_REVIEW"))
        self.assertEqual(new["parent_key"],"old");self.assertNotEqual(new["decision_id"],old["decision_id"])
        self.assertEqual(self.store.replay("old"),old)
    def test_recompute_uses_recorded_policy_without_mutation(self):
        self.store.decide("old",PAYLOAD);self.store.activate("BR-001/v2");before=self.counts()
        r=self.store.recompute("old")
        self.assertEqual((r["status"],r["recorded_policy"]),("MATCH","BR-001/v1"));self.assertEqual(self.counts(),before)
    def test_activation_and_history_survive_restart(self):
        old=self.store.decide("old",PAYLOAD)["record"];self.store.activate("BR-001/v2")
        self.store.close();self.store=ledger.PolicyStore(self.db,CATALOG);self.addCleanup(self.store.close)
        self.assertEqual(self.store.active_policy(),"BR-001/v2");self.assertEqual(self.store.replay("old"),old)
    def test_original_payload_survives_canonical_retry(self):
        old=self.store.decide("old",{**PAYLOAD,"amount_eur":"4000.0"})["record"]
        again=self.store.decide("old",PAYLOAD)["record"]
        self.assertEqual(again,old);self.assertEqual(again["payload"]["amount_eur"],"4000.0")
    def test_history_cannot_be_updated_or_deleted(self):
        self.store.decide("old",PAYLOAD)
        with self.assertRaises(sqlite3.IntegrityError):self.store.conn.execute("DELETE FROM decisions")
    def seed_legacy(self):
        path=self.db.parent/"legacy.sqlite"
        raw={"request_key":"legacy","payload_json":ledger.canonical(PAYLOAD),"policy_json":ledger.canonical(CATALOG["BR-001/v1"]),"decision_json":ledger.canonical(ledger.outcome(PAYLOAD,CATALOG["BR-001/v1"]))}
        with sqlite3.connect(path) as con:
            con.execute("CREATE TABLE legacy_decisions(request_key TEXT PRIMARY KEY,payload_json TEXT,policy_json TEXT,decision_json TEXT)")
            con.execute("INSERT INTO legacy_decisions VALUES(?,?,?,?)",tuple(raw.values()))
            con.execute("PRAGMA user_version=1");con.execute("PRAGMA application_id=1129337137")
        proof={"schema":"cp11-legacy-provenance/v1","origin":"SYNTHETIC_BROWNFIELD_FIXTURE","source_id":"B3-legacy-fixture","rows_sha256":ledger.digest(ledger.canonical([raw]))}
        return path,raw,proof
    def test_explicit_migration_preserves_legacy_payload(self):
        path,raw,proof=self.seed_legacy();r=ledger.migrate_legacy(path,CATALOG,proof)
        self.assertTrue(r["original_table_preserved"])
        store=ledger.PolicyStore(path,CATALOG)
        try:self.assertEqual(store.replay("legacy")["payload_json"],raw["payload_json"])
        finally:store.close()
        with sqlite3.connect(path) as con:self.assertEqual(con.execute("SELECT payload_json FROM legacy_decisions").fetchone()[0],raw["payload_json"])
    def test_missing_provenance_stops_without_mutation(self):
        path,raw,proof=self.seed_legacy();before=path.read_bytes()
        with self.assertRaises(ledger.HistoryError):ledger.migrate_legacy(path,CATALOG,{})
        self.assertEqual(path.read_bytes(),before)
    def test_non_ascii_numeric_input_is_outside_history_api(self):
        with self.assertRaises(ledger.HistoryError):self.store.decide("bad",{**PAYLOAD,"amount_eur":"４０００"})
