"""Negative controls for the trace-era explanation; no protocol is simulated."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from inspect_trace import PREFIX, inspect


class TraceInspectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        original = Path(__file__).parent / "observed/attempt_02_local_stdio_pass"
        for name in ("COMPARISON.json", "client_to_server.jsonl", "server_to_client.jsonl"):
            shutil.copy2(original / name, self.root / name)

    def tearDown(self):
        self.temporary.cleanup()

    def rewrite_requests(self, mutation):
        path = self.root / "client_to_server.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        mutation(rows)
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))

    def test_retained_exchange_is_modern_and_identities_are_distinct(self):
        result = inspect(self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["legacy_initialize_observed"])
        self.assertEqual(result["sdk_distribution_version"], "2.3.0")
        self.assertEqual(result["wire_client_info"]["version"], "0.1.0")

    def test_wrong_per_request_version_is_not_hidden_by_receipt(self):
        self.rewrite_requests(lambda rows: rows[2]["params"]["_meta"].update({PREFIX + "protocolVersion": "2025-11-25"}))
        self.assertIn("VERSION_METADATA_MISSING_OR_CHANGED:3", inspect(self.root)["issues"])

    def test_missing_capabilities_is_rejected(self):
        self.rewrite_requests(lambda rows: rows[1]["params"]["_meta"].pop(PREFIX + "clientCapabilities"))
        self.assertIn("CAPABILITIES_METADATA_MISSING:2", inspect(self.root)["issues"])

    def test_legacy_opening_cannot_be_called_the_same_exchange(self):
        self.rewrite_requests(lambda rows: rows[0].update({"method": "initialize"}))
        result = inspect(self.root)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["legacy_initialize_observed"])


if __name__ == "__main__":
    unittest.main()
