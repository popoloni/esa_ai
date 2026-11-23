import unittest, tempfile, hashlib
from pathlib import Path
import booking
from reservation_report import build_report
class ReportContract(unittest.TestCase):
    def test_history_and_current_state_remain_distinct(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"book.sqlite";booking.init_db(p)
            request=dict(trusted_member_id="m-1",asset_id="A",starts_at="2025-05-16T09:00:00Z",ends_at="2025-05-16T10:00:00Z",idempotency_key="k-1")
            out=booking.reserve(p,**request);before=p.read_bytes()
            self.assertEqual(build_report(p,out.reservation_id),{"found":True,"reservation":{"reservation_id":out.reservation_id,**request},"current":{"state":"active","version":1}})
            self.assertEqual(p.read_bytes(),before)
            booking.cancel(p,out.reservation_id,trusted_member_id="m-1",expected_version=1);before=p.read_bytes()
            self.assertEqual(build_report(p,out.reservation_id),{"found":True,"reservation":{"reservation_id":out.reservation_id,**request},"current":{"state":"cancelled","version":2}})
            self.assertEqual(p.read_bytes(),before)
    def test_absent_is_an_observation(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"book.sqlite";booking.init_db(p);before=p.read_bytes()
            self.assertEqual(build_report(p,999),{"found":False,"reservation":None,"current":None})
            self.assertEqual(p.read_bytes(),before)
    def test_missing_storage_is_not_created(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"missing.sqlite"
            with self.assertRaises(sqlite3.OperationalError):build_report(p,1)
            self.assertFalse(p.exists())
