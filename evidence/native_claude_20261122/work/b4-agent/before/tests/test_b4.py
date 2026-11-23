from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import ledger,incident
CATALOG={v:{"version":v,"threshold_eur":t,"algorithm":"TREASURY_THRESHOLD_V1"} for v,t in (("BR-001/v1","5000.00"),("BR-001/v2","3000.00"))}
PAYLOAD={"amount_eur":"4000.00","beneficiary_id":"supplier_41"}
class WrongLedger(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        self.good,self.wrong=self.root/"expected.sqlite",self.root/"wrong.sqlite"
        for path in (self.good,self.wrong):
            store=ledger.PolicyStore(path,CATALOG)
            try:
                store.decide("old",PAYLOAD)
                if path==self.good:
                    store.decide("anchor",{**PAYLOAD,"amount_eur":"12.00"});store.activate("BR-001/v2")
            finally:store.close()
    def diagnosis(self):return incident.diagnose(self.wrong,self.good,expected_policy="BR-001/v2",anchor_key="anchor")
    def test_same_code_wrong_state_is_identified(self):
        before=(self.good.read_bytes(),self.wrong.read_bytes());r=self.diagnosis()
        self.assertEqual(r["status"],"WRONG_LEDGER")
        self.assertEqual(set(r["issues"]),{"STATE_PATH_MISMATCH","ACTIVE_POLICY_MISMATCH","ANCHOR_MISSING"})
        self.assertEqual((self.good.read_bytes(),self.wrong.read_bytes()),before)
    def test_deterministic_id_does_not_establish_same_ledger(self):
        good=incident.inspect_ledger(self.good);wrong=incident.inspect_ledger(self.wrong)
        a=next(x for x in good["decisions"] if x["request_id"]=="old")
        b=next(x for x in wrong["decisions"] if x["request_id"]=="old")
        self.assertEqual(a["decision_id"],b["decision_id"])
        self.assertNotEqual(good["path"],wrong["path"])
        self.assertEqual(self.diagnosis()["status"],"WRONG_LEDGER")
    def test_missing_path_is_not_initialized(self):
        path=self.root/"missing.sqlite"
        with self.assertRaises(FileNotFoundError):incident.inspect_ledger(path)
        self.assertFalse(path.exists())
    def test_recovery_plan_does_not_merge_or_authorize(self):
        r=incident.recovery_plan(self.diagnosis())
        self.assertFalse(r["automatic_merge"]);self.assertFalse(r["production_authorized"])
        self.assertEqual(r["reconciliation"],"PENDING_OWNER_DECISION")
        self.assertEqual(set(r["preserve_ledgers"]),{str(self.good),str(self.wrong)})
    def test_expected_binding_is_clean_positive_control(self):
        r=incident.diagnose(self.good,self.good,expected_policy="BR-001/v2",anchor_key="anchor")
        self.assertEqual(r["status"],"EXPECTED_LEDGER_SELECTED");self.assertEqual(r["issues"],[])
    def test_recovery_cost_includes_failed_attempt(self):
        r=incident.cost_summary([{"cost_eur":"1.2","minutes":"8"},{"cost_eur":"0.8","minutes":"12"}],1)
        self.assertEqual(r["total_cost_eur"],"2.0");self.assertEqual(r["minutes_per_accepted"],"20")


class RecoveryConsumerContract(unittest.TestCase):
    def test_proposed_configuration_binding_has_explicit_consumer_field(self):
        import json
        from incident import diagnose, recovery_plan
        import ledger
        with TemporaryDirectory() as temp:
            expected=Path(temp)/"expected.sqlite";wrong=Path(temp)/"wrong.sqlite"
            catalog=CATALOG
            for path in (expected,wrong):
                store=ledger.PolicyStore(path,catalog)
                store.decide("old",{"amount_eur":"4000.00","beneficiary_id":"supplier_41"})
                if path==expected:
                    store.decide("anchor",{"amount_eur":"12.00","beneficiary_id":"supplier_41"})
                    store.activate("BR-001/v2")
                store.close()
            before={str(p):p.read_bytes() for p in (expected,wrong)}
            plan=recovery_plan(diagnose(wrong,expected,expected_policy="BR-001/v2",anchor_key="anchor"))
            self.assertEqual(plan["restore_configuration_to"],str(expected.resolve()))
            self.assertIs(plan["automatic_merge"],False)
            self.assertIs(plan["production_authorized"],False)
            self.assertEqual({str(p):p.read_bytes() for p in (expected,wrong)},before)
