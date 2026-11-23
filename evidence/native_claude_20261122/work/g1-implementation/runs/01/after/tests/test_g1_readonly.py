"""Public read behavior from G1-OD-01; no internal schema dependency."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest
import booking

class ReadOnlyLookup(unittest.TestCase):
    def test_missing_database_is_not_created(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "missing ?# file.sqlite"
            with self.assertRaises(sqlite3.OperationalError):
                booking.get_reservation(path, 1)
            self.assertFalse(path.exists(), "reading must not create storage")

    def test_uri_special_characters_and_unchanged_database(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "present ?# file.sqlite"
            booking.init_db(path)
            before = path.read_bytes()
            self.assertIsNone(booking.get_reservation(path, -77))
            self.assertEqual(path.read_bytes(), before)
