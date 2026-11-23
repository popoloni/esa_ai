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


import sqlite3
import legacy_g1
import legacy_g1_json

class ReservationMigration(unittest.TestCase):
    def test_both_supplied_g1_schemas_preserve_record_and_identity(self):
        for source in (legacy_g1, legacy_g1_json):
            with self.subTest(schema=source.__name__), TemporaryDirectory() as temp:
                path = Path(temp)/"old.sqlite"
                source.init_db(path)
                request = dict(trusted_member_id="member-1",asset_id="A",starts_at=S,ends_at=E,idempotency_key="old-key")
                original = source.reserve(path,**request)
                booking.init_db(path)
                self.assertEqual(booking.get_reservation(path, original.reservation_id),
                                 {"reservation_id":original.reservation_id,**request})
                repeated = booking.reserve(path,**request)
                self.assertTrue(repeated.replayed)
                self.assertEqual(repeated.reservation_id,original.reservation_id)
                booking.init_db(path)
                self.assertEqual(booking.get_reservation(path,original.reservation_id)["asset_id"],"A")

    def test_duplicate_legacy_identity_rolls_back_migration(self):
        with TemporaryDirectory() as temp:
            path = Path(temp)/"conflict.sqlite"
            legacy_g1.init_db(path)
            request = dict(trusted_member_id="member-1",asset_id="A",starts_at=S,ends_at=E,idempotency_key="same")
            legacy_g1.reserve(path,**request)
            legacy_g1.reserve(path,**{**request,"asset_id":"B"})
            before = path.read_bytes()
            with self.assertRaises(sqlite3.IntegrityError):booking.init_db(path)
            self.assertEqual(path.read_bytes(),before)

    def test_read_of_missing_storage_does_not_create_file(self):
        with TemporaryDirectory() as temp:
            path = Path(temp)/"missing ?#.sqlite"
            with self.assertRaises(sqlite3.OperationalError):booking.get_reservation(path,1)
            self.assertFalse(path.exists())

    def test_invalid_or_overlapping_legacy_rows_require_owner_mapping(self):
        cases = (
            {"starts_at":"not-a-timestamp"},
            {"asset_id":""},
            {"idempotency_key":"other-key"},
        )
        for change in cases:
            with self.subTest(change=change), TemporaryDirectory() as temp:
                path=Path(temp)/"ambiguous.sqlite"
                legacy_g1.init_db(path)
                request=dict(trusted_member_id="member-1",asset_id="A",starts_at=S,ends_at=E,idempotency_key="first-key")
                legacy_g1.reserve(path,**request)
                legacy_g1.reserve(path,**{**request,**change})
                before=path.read_bytes()
                with self.assertRaises(ValueError):booking.init_db(path)
                self.assertEqual(path.read_bytes(),before)

    def test_unknown_or_dual_legacy_schema_is_not_guessed(self):
        for dual in (False,True):
            with self.subTest(dual=dual), TemporaryDirectory() as temp:
                path=Path(temp)/"unmapped.sqlite"
                if dual:
                    legacy_g1.init_db(path);legacy_g1_json.init_db(path)
                else:
                    with sqlite3.connect(path) as con:con.execute("CREATE TABLE something_else(id INTEGER)")
                before=path.read_bytes()
                with self.assertRaises(ValueError):booking.init_db(path)
                self.assertEqual(path.read_bytes(),before)


class RecordedG1Migration(unittest.TestCase):
    def test_retained_public_column_schema_preserves_read_replay_and_reinit(self):
        import legacy_g1_recorded as original
        with TemporaryDirectory() as temp:
            path = Path(temp) / "actual-g1.sqlite"
            request = dict(trusted_member_id="member-1", asset_id="A", starts_at=S,
                           ends_at=E, idempotency_key="retained-key")
            original.init_db(path)
            saved = original.reserve(path, **request)
            expected = {"reservation_id": saved.reservation_id, **request}
            booking.init_db(path)
            self.assertEqual(booking.get_reservation(path, saved.reservation_id), expected)
            replay = booking.reserve(path, **request)
            self.assertEqual((replay.status, replay.reservation_id, replay.replayed),
                             (200, saved.reservation_id, True))
            booking.init_db(path)
            self.assertEqual(booking.get_reservation(path, saved.reservation_id), expected)
            with sqlite3.connect(path) as con:
                expected_columns = ["reservation_id", "trusted_member_id", "asset_id", "starts_at", "ends_at", "idempotency_key"]
                preserved = []
                for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
                    quoted = '"' + name.replace('"', '""') + '"'
                    columns = [row[1] for row in con.execute('PRAGMA table_info(' + quoted + ')')]
                    if columns == expected_columns:
                        rows = con.execute('SELECT * FROM ' + quoted).fetchall()
                        if rows == [(saved.reservation_id, "member-1", "A", S, E, "retained-key")]:
                            preserved.append(name)
                self.assertTrue(preserved, "The original column representation and rows must survive; its archive name is not prescribed")

    def test_invalid_retained_public_column_record_refuses_without_byte_change(self):
        import legacy_g1_recorded as original
        with TemporaryDirectory() as temp:
            path = Path(temp) / "invalid-actual-g1.sqlite"
            original.init_db(path)
            original.reserve(path, trusted_member_id="member-1", asset_id="A",
                             starts_at="bad", ends_at=E, idempotency_key="retained-key")
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                booking.init_db(path)
            self.assertEqual(path.read_bytes(), before)
