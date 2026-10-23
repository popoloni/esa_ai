"""Self-authored focused checks for CSV-001/v1; not independent acceptance."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "work"))
from api import orders_response

FIELDS = ["order_id", "status", "customer", "amount_eur", "note"]


class ContractChecks(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads((BASE / "work/orders.json").read_text())

    def test_existing_json_baseline(self):
        baseline = json.loads((BASE / "INITIAL_JSON.output.txt").read_text())
        self.assertEqual(orders_response(self.rows, "alice"),
                         {"content_type": "application/json", "body": baseline})

    def test_actor_status_and_order_matrix(self):
        cases = [
            ("alice", None, ["A1", "A2"]),
            ("alice", "open", ["A1"]),
            ("alice", "closed", ["A2"]),
            ("alice", "missing", []),
            ("bob", None, ["B1"]),
            ("bob", "open", ["B1"]),
            ("bob", "closed", []),
            ("unknown", None, []),
        ]
        originals = {row["order_id"]: row for row in self.rows}
        for actor, status, expected_ids in cases:
            with self.subTest(actor=actor, status=status):
                response = orders_response(self.rows, actor, "csv", status)
                self.assertEqual(response["content_type"], "text/csv; charset=utf-8")
                reader = csv.DictReader(io.StringIO(response["body"], newline=""))
                parsed = list(reader)
                self.assertEqual(reader.fieldnames, FIELDS)
                self.assertEqual([row["order_id"] for row in parsed], expected_ids)
                expected = [{key: originals[oid][key] for key in FIELDS}
                            for oid in expected_ids]
                self.assertEqual(parsed, expected)
                self.assertEqual(orders_response(self.rows, actor, "json", status)["body"],
                                 expected)

    def test_header_without_rows(self):
        for rows, actor in [(self.rows, "unknown"), ([], "alice")]:
            with self.subTest(actor=actor, count=len(rows)):
                body = orders_response(rows, actor, "csv")["body"]
                self.assertEqual(list(csv.reader(io.StringIO(body, newline=""))), [FIELDS])

    def test_literal_roundtrip_and_source_nonmutation(self):
        values = ["comma, value", 'double "quote"', "line one\nline two",
                  "CRLF\r\ntext", "Caffè 東京", "", "=SUM(A1:A2)",
                  "+formula", "-formula", "@formula", "'literal apostrophe"]
        rows = []
        for number, value in enumerate(values):
            rows.append({"owner": "alice", "order_id": str(number), "status": "open",
                         "customer": value, "amount_eur": "01.20", "note": value})
        before = copy.deepcopy(rows)
        body = orders_response(rows, "alice", "csv", "open")["body"]
        parsed = list(csv.DictReader(io.StringIO(body, newline="")))
        expected = [{key: row[key] for key in FIELDS} for row in before]
        self.assertEqual(parsed, expected)
        self.assertEqual(rows, before)
        orders_response(rows, "alice", "json")
        self.assertEqual(rows, before)

    def test_unsupported_formats(self):
        for value in ["xml", "CSV", "", None]:
            with self.subTest(format=value):
                with self.assertRaises(ValueError):
                    orders_response(self.rows, "alice", value)

    def test_protected_inputs_unchanged(self):
        start = json.loads((BASE / "START.json").read_text())
        for name, expected in start["protected_inputs"].items():
            with self.subTest(file=name):
                actual = hashlib.sha256((BASE / "work" / name).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
