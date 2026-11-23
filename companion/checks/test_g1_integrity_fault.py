"""Candidate-specific fault probe, separate from public G1 slice acceptance.

The constructed IntegrityError pack and supplied solutions use booking.sqlite3.
This probe intercepts that known seam to demonstrate swallowed storage failure;
it does not impose the seam or internal schema on arbitrary learner solutions.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest
from unittest.mock import patch
import booking


class IntegrityFaultProbe(unittest.TestCase):
    def test_storage_integrity_failure_propagates(self):
        with TemporaryDirectory() as temp:
            db = Path(temp) / "fault.db"
            booking.init_db(db)
            real_connect = sqlite3.connect
            injected = []

            class ConnectionFault:
                def __init__(self, con):
                    self.con = con
                def __getattr__(self, name):
                    return getattr(self.con, name)
                def __enter__(self):
                    self.con.__enter__()
                    return self
                def __exit__(self, *args):
                    return self.con.__exit__(*args)
                def execute(self, sql, *args):
                    if sql.lstrip().upper().startswith("INSERT"):
                        injected.append("insert")
                        raise sqlite3.IntegrityError("injected integrity fault")
                    return self.con.execute(sql, *args)

            def connect(*args, **kwargs):
                return ConnectionFault(real_connect(*args, **kwargs))

            with patch.object(booking.sqlite3, "connect", side_effect=connect):
                with self.assertRaisesRegex(sqlite3.IntegrityError, "injected integrity fault"):
                    booking.reserve(db, trusted_member_id="member-1", asset_id="A",
                                    starts_at="2025-05-16T09:00:00Z", ends_at="2025-05-16T10:00:00Z",
                                    idempotency_key="key-1")
            self.assertEqual(injected, ["insert"], "The intended fault seam must be exercised")
