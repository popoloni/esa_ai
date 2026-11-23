"""Tests derive expected behavior from the independent reviewed contract.

These are not tests of authentication, HTTP routing, remote agents or throughput.
"""
import concurrent.futures
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest

from booking import init_db, reserve

S = '2026-11-02T09:00:00Z'
E = '2026-11-02T10:00:00Z'


class ReservationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'reserve.db'
        init_db(self.db)

    def req(self, member='member-1', key='key-1', start=S, end=E, asset='A'):
        return reserve(self.db, trusted_member_id=member,
                       asset_id=asset, starts_at=start, ends_at=end,
                       idempotency_key=key)

    def row_count(self):
        with sqlite3.connect(self.db) as con:
            return con.execute('SELECT COUNT(*) FROM reservations').fetchone()[0]

    def test_first_reservation_confirms(self):
        result = self.req()
        self.assertEqual((result.status, result.code), (201, 'confirmed'))
        self.assertIsNotNone(result.reservation_id)
        self.assertEqual(self.row_count(), 1)

    def test_overlap_fails_without_insert(self):
        self.req()
        result = self.req(member='member-2', key='key-2',
                          start='2026-11-02T09:30:00Z', end='2026-11-02T10:30:00Z')
        self.assertEqual((result.status, result.code), (409, 'interval-conflict'))
        self.assertEqual(self.row_count(), 1)

    def test_adjacent_reservation_succeeds(self):
        self.req()
        result = self.req(member='member-2', key='key-2',
                          start=E, end='2026-11-02T11:00:00Z')
        self.assertEqual(result.status, 201)
        self.assertEqual(self.row_count(), 2)

    def test_different_assets_do_not_conflict(self):
        self.req()
        result = self.req(member='member-2', key='key-2', asset='B')
        self.assertEqual(result.status, 201)
        self.assertEqual(self.row_count(), 2)

    def test_same_request_key_replays_original(self):
        original = self.req()
        repeat = self.req()
        self.assertEqual(repeat.status, 200)
        self.assertEqual(original.reservation_id, repeat.reservation_id)
        self.assertTrue(repeat.replayed)
        self.assertEqual(self.row_count(), 1)

    def test_changed_request_with_same_key_fails(self):
        self.req()
        change = self.req(end='2026-11-02T11:00:00Z')
        self.assertEqual((change.status, change.code), (409, 'idempotency-key-reused'))
        self.assertEqual(self.row_count(), 1)

    def test_invalid_zero_or_reverse_interval_has_no_effect(self):
        self.assertEqual(self.req(end=S).status, 422)
        self.assertEqual(self.req(start=E, end=S).status, 422)
        self.assertEqual(self.row_count(), 0)

    def test_duration_limit_and_timestamp_format(self):
        self.assertEqual(self.req(end='2026-11-03T09:00:01Z').status, 422)
        self.assertEqual(self.req(start='2026-11-02T09:00:00+00:00').status, 422)
        self.assertEqual(self.row_count(), 0)

    def test_other_member_same_key_is_independent_but_conflicts_on_slot(self):
        self.req()
        result = self.req(member='member-2', key='key-1')
        self.assertEqual(result.code, 'interval-conflict')

    def test_two_writers_do_not_both_confirm_same_slot(self):
        def worker(n):
            return self.req(member=f'member-{n}',key=f'key-{n}')
        # Both independent calls use their own SQLite connections and the same file.
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(worker, [10, 11]))
        self.assertEqual(sorted(r.status for r in results), [201,409])
        self.assertEqual(self.row_count(), 1)


if __name__=='__main__':
    unittest.main()
