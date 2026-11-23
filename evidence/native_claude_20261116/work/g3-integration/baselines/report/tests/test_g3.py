from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import booking
import legacy_booking
S="2025-05-16T09:00:00Z"
E="2025-05-16T10:00:00Z"
REQUEST=dict(trusted_member_id="member-1",asset_id="A",starts_at=S,ends_at=E,idempotency_key="key")
class Cancellation(unittest.TestCase):
    def setUp(self):
        t=TemporaryDirectory();self.addCleanup(t.cleanup);self.db=Path(t.name)/"reserve.sqlite"
        legacy_booking.init_db(self.db)
        self.original=legacy_booking.reserve(self.db,**REQUEST)
        self.record=legacy_booking.get_reservation(self.db,self.original.reservation_id)
        booking.init_db(self.db)
    def test_migration_preserves_old_public_record(self):
        self.assertEqual(booking.get_reservation(self.db,self.original.reservation_id),self.record)
        self.assertEqual(booking.reservation_status(self.db,self.original.reservation_id),{"state":"active","version":1})
    def test_other_member_cannot_cancel(self):
        result=booking.cancel(self.db,self.original.reservation_id,trusted_member_id="intruder",expected_version=1)
        self.assertEqual((result["status"],result["code"]),(403,"not-owner"))
        self.assertEqual(booking.reservation_status(self.db,self.original.reservation_id)["state"],"active")
    def test_stale_version_cannot_change_state(self):
        result=booking.cancel(self.db,self.original.reservation_id,trusted_member_id="member-1",expected_version=0)
        self.assertEqual(result["code"],"stale-version")
        self.assertEqual(booking.reservation_status(self.db,self.original.reservation_id)["version"],1)
    def test_cancel_releases_slot_without_erasing_history(self):
        result=booking.cancel(self.db,self.original.reservation_id,trusted_member_id="member-1",expected_version=1)
        self.assertEqual((result["code"],result["version"]),("cancelled",2))
        self.assertEqual(booking.get_reservation(self.db,self.original.reservation_id),self.record)
        fresh=booking.reserve(self.db,**{**REQUEST,"trusted_member_id":"member-2","idempotency_key":"new"})
        self.assertEqual(fresh.status,201)
    def test_repeat_with_current_version_is_idempotent(self):
        booking.cancel(self.db,self.original.reservation_id,trusted_member_id="member-1",expected_version=1)
        second=booking.cancel(self.db,self.original.reservation_id,trusted_member_id="member-1",expected_version=2)
        self.assertEqual((second["code"],second["version"]),("already-cancelled",2))
        stale=booking.cancel(self.db,self.original.reservation_id,trusted_member_id="member-1",expected_version=1)
        self.assertEqual(stale["code"],"stale-version")
    def test_retry_original_operation_does_not_revive_cancelled_row(self):
        booking.cancel(self.db,self.original.reservation_id,trusted_member_id="member-1",expected_version=1)
        retry=booking.reserve(self.db,**REQUEST)
        self.assertTrue(retry.replayed)
        self.assertEqual(retry.reservation_id,self.original.reservation_id)
        self.assertEqual(booking.reservation_status(self.db,self.original.reservation_id)["state"],"cancelled")
    def test_missing_id_is_not_found(self):
        self.assertEqual(booking.cancel(self.db,999,trusted_member_id="member-1",expected_version=1)["status"],404)
        self.assertIsNone(booking.reservation_status(self.db,999))
