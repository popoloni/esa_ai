from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest
import booking
from operations import diagnose,cost_summary
class OperationalEvidence(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.db=Path(t.name)/"reserve.sqlite"
        booking.init_db(self.db)
        booking.reserve(self.db,trusted_member_id="m1",asset_id="A",starts_at="2025-05-16T09:00:00Z",ends_at="2025-05-16T10:00:00Z",idempotency_key="one")
    def test_clean_storage_is_observed_without_mutation(self):
        before=self.db.read_bytes();result=diagnose(self.db)
        self.assertEqual(result["diagnosis"],"NO_ACTIVE_OVERLAP_OBSERVED")
        self.assertEqual(result["counts"],{"active":1})
        self.assertEqual(self.db.read_bytes(),before)
    def test_active_overlap_is_detected_not_repaired(self):
        from g4_fixture import insert_overlap
        insert_overlap(self.db)
        before=self.db.read_bytes();result=diagnose(self.db)
        self.assertEqual(result["diagnosis"],"ACTIVE_OVERLAP")
        self.assertEqual(result["active_overlap_pairs"],[[1,2]])
        self.assertEqual(self.db.read_bytes(),before)
    def test_cancelled_row_does_not_create_false_alarm(self):
        booking.cancel(self.db,1,trusted_member_id="m1",expected_version=1)
        booking.reserve(self.db,trusted_member_id="m2",asset_id="A",starts_at="2025-05-16T09:00:00Z",ends_at="2025-05-16T10:00:00Z",idempotency_key="two")
        self.assertEqual(diagnose(self.db)["active_overlap_pairs"],[])
    def test_missing_path_is_not_created(self):
        missing=self.db.parent/"missing.sqlite"
        with self.assertRaises((FileNotFoundError,sqlite3.OperationalError)):diagnose(missing)
        self.assertFalse(missing.exists())
    def test_all_attempts_count_toward_accepted_outcome_cost(self):
        r=cost_summary([{"cost_eur":"2.20","minutes":"12"},{"cost_eur":"0.80","minutes":"8"}],1)
        self.assertEqual(r["total_cost_eur"],"3.00")
        self.assertEqual(r["cost_per_accepted_eur"],"3.00")
        self.assertEqual(r["minutes_per_accepted"],"20")
    def test_zero_accepted_is_not_zero_unit_cost(self):
        r=cost_summary([{"cost_eur":"1","minutes":"5"}],0)
        self.assertIsNone(r["cost_per_accepted_eur"])
        self.assertEqual(r["status"],"NO_ACCEPTED_OUTCOME")
    def test_invalid_cost_or_time_is_refused(self):
        for value in ("NaN","Infinity","-1"):
            with self.subTest(value=value),self.assertRaises(ValueError):cost_summary([{"cost_eur":value,"minutes":1}],1)

    def test_nonnumeric_cost_and_time_raise_value_error(self):
        for field in ("cost_eur", "minutes"):
            values = {"cost_eur": "1.25", "minutes": "2"}
            values[field] = "not-a-number"
            with self.subTest(field=field), self.assertRaises(ValueError):
                cost_summary([values], 1)
        positive = cost_summary([{"cost_eur": "1.25", "minutes": "2"}], 1)
        self.assertEqual(positive["total_cost_eur"], "1.25")
        self.assertEqual(positive["total_minutes"], "2")

    def test_failed_attempts_remain_in_the_cost_numerator(self):
        result = cost_summary([
            {"cost_eur": "2.20", "minutes": "12", "status": "FAILED"},
            {"cost_eur": "0.80", "minutes": "8", "status": "ACCEPTED"}], 1)
        self.assertEqual(result["total_cost_eur"], "3.00")
        self.assertEqual(result["cost_per_accepted_eur"], "3.00")
        self.assertEqual(result["minutes_per_accepted"], "20")
        self.assertEqual(result["attempts"], 2)

    def test_reference_schema_remains_explicitly_supported(self):
        import reference_g3
        from g4_fixture import insert_overlap
        with TemporaryDirectory() as temp:
            p=Path(temp)/"reference.sqlite";reference_g3.init_db(p)
            reference_g3.reserve(p,trusted_member_id="m1",asset_id="A",starts_at="2025-05-16T09:00:00Z",ends_at="2025-05-16T10:00:00Z",idempotency_key="one")
            insert_overlap(p);before=p.read_bytes()
            self.assertEqual(diagnose(p)["active_overlap_pairs"],[[1,2]])
            self.assertEqual(p.read_bytes(),before)

    def test_version_number_alone_does_not_authorize_unknown_schema(self):
        with TemporaryDirectory() as temp:
            p=Path(temp)/"unmapped.sqlite"
            with sqlite3.connect(p) as con:
                con.execute("CREATE TABLE unrelated(id INTEGER)")
                con.execute("PRAGMA user_version=3")
            before=p.read_bytes()
            with self.assertRaises((ValueError,sqlite3.OperationalError)):
                diagnose(p)
            self.assertEqual(p.read_bytes(),before)
