"""G1/I01 acceptance through the public API; no table or column inspection."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import booking

REQUEST = {"trusted_member_id": "member-1", "asset_id": "A",
           "starts_at": "2025-05-16T09:00:00Z", "ends_at": "2025-05-16T10:00:00Z",
           "idempotency_key": "key-1"}


class ReservationSlice(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.db = Path(temporary.name) / "reserve.db"
        booking.init_db(self.db)

    def confirm(self, request):
        result = booking.reserve(self.db, **request)
        self.assertEqual((result.status, result.code), (201, "confirmed"))
        self.assertIsInstance(result.reservation_id, int)
        self.assertGreater(result.reservation_id, 0)
        self.assertFalse(result.replayed)
        self.assertEqual(booking.get_reservation(self.db, result.reservation_id),
                         {"reservation_id": result.reservation_id, **request})
        return result

    def test_first_reservation_confirms_and_public_read_matches(self):
        self.confirm(REQUEST)

    def test_missing_reservation_returns_none(self):
        self.assertIsNone(booking.get_reservation(self.db, -1))

    def test_quoted_identifiers_round_trip(self):
        self.confirm({**REQUEST, "trusted_member_id": "member'1",
                      "asset_id": "A's drill", "idempotency_key": "key'1"})

    def test_init_db_preserves_existing_reservation(self):
        result = self.confirm(REQUEST)
        booking.init_db(self.db)
        self.assertEqual(booking.get_reservation(self.db, result.reservation_id),
                         {"reservation_id": result.reservation_id, **REQUEST})
