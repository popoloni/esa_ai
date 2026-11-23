"""Full RES-001/v1 diagnostic via public outcomes and reads.

These ten methods adapt the historical scenarios. They do not inspect tables
or prove absence of invisible extra rows. The original ten remain unchanged.
"""
import concurrent.futures
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import booking

S = "2025-05-16T09:00:00Z"
E = "2025-05-16T10:00:00Z"


class ReservationFullAPI(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.db = Path(temporary.name) / "reserve.db"
        booking.init_db(self.db)

    def req(self, member="member-1", key="key-1", start=S, end=E, asset="A"):
        return booking.reserve(self.db, trusted_member_id=member, asset_id=asset,
                               starts_at=start, ends_at=end, idempotency_key=key)

    def test_first_reservation_confirms(self):
        result = self.req()
        self.assertEqual((result.status, result.code), (201, "confirmed"))
        self.assertEqual(booking.get_reservation(self.db, result.reservation_id),
                         {"reservation_id": result.reservation_id, "trusted_member_id": "member-1",
                          "asset_id": "A", "starts_at": S, "ends_at": E, "idempotency_key": "key-1"})

    def test_overlap_fails_without_insert(self):
        first = self.req()
        original = booking.get_reservation(self.db, first.reservation_id)
        result = self.req(member="member-2", key="key-2",
                          start="2025-05-16T09:30:00Z", end="2025-05-16T10:30:00Z")
        self.assertEqual((result.status, result.code), (409, "interval-conflict"))
        self.assertIsNone(result.reservation_id)
        self.assertEqual(booking.get_reservation(self.db, first.reservation_id), original)

    def test_adjacent_reservation_succeeds(self):
        first = self.req()
        adjacent = self.req(member="member-2", key="key-2", start=E, end="2025-05-16T11:00:00Z")
        self.assertEqual(adjacent.status, 201)
        self.assertNotEqual(first.reservation_id, adjacent.reservation_id)
        self.assertEqual(booking.get_reservation(self.db, adjacent.reservation_id)["starts_at"], E)

    def test_different_assets_do_not_conflict(self):
        self.req()
        different = self.req(member="member-2", key="key-2", asset="B")
        self.assertEqual(different.status, 201)
        self.assertEqual(booking.get_reservation(self.db, different.reservation_id)["asset_id"], "B")

    def test_same_request_key_replays_original(self):
        original = self.req()
        repeated = self.req()
        self.assertEqual(repeated.status, 200)
        self.assertEqual(original.reservation_id, repeated.reservation_id)
        self.assertTrue(repeated.replayed)

    def test_changed_request_with_same_key_fails(self):
        first = self.req()
        change = self.req(end="2025-05-16T11:00:00Z")
        self.assertEqual((change.status, change.code), (409, "idempotency-key-reused"))
        self.assertIsNone(change.reservation_id)
        self.assertEqual(booking.get_reservation(self.db, first.reservation_id)["ends_at"], E)

    def test_invalid_zero_or_reverse_interval_has_no_effect(self):
        for result in (self.req(end=S), self.req(start=E, end=S)):
            self.assertEqual(result.status, 422)
            self.assertIsNone(result.reservation_id)

    def test_duration_limit_and_timestamp_format(self):
        for result in (self.req(end="2026-11-03T09:00:01Z"), self.req(start="2025-05-16T09:00:00+00:00")):
            self.assertEqual(result.status, 422)
            self.assertIsNone(result.reservation_id)

    def test_other_member_same_key_is_independent_but_conflicts_on_slot(self):
        self.req()
        result = self.req(member="member-2", key="key-1")
        self.assertEqual((result.status, result.code), (409, "interval-conflict"))
        self.assertIsNone(result.reservation_id)

    def test_two_writers_do_not_both_confirm_same_slot(self):
        def worker(number):
            return self.req(member=f"member-{number}", key=f"key-{number}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(worker, [10, 11]))
        self.assertEqual(sorted(result.status for result in results), [201, 409])
        confirmed = [result for result in results if result.status == 201][0]
        self.assertIsNotNone(booking.get_reservation(self.db, confirmed.reservation_id))
