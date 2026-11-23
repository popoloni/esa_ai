"""B1-API/v2 obligations read from the owner decision, not inferred from code."""
import unittest
from treasury import routing

class MonetaryTextV2(unittest.TestCase):
    def test_valid_spellings_preserve_numeric_policy(self):
        for value in ("4000", "004000.00", "+4999.99", "0.01", "+0.1"):
            with self.subTest(value=value):
                r = routing.assess(value)
                self.assertEqual((r.route, r.reason, r.policy_version),
                                 ("STANDARD_QUEUE", "BELOW_LIMIT", "BR-001/v1"))

    def test_boundary_and_larger_values_require_review(self):
        for value in ("5000", "5000.0", "+005000.00", "99999999999999999999999999999999"):
            with self.subTest(value=value):
                self.assertEqual(routing.assess(value).route, "HUMAN_REVIEW")

    def test_nonpositive_values_are_rejected(self):
        for value in ("0", "-0", "+0.00", "-1.00"):
            with self.subTest(value=value):
                self.assertEqual(routing.assess(value).reason, "INVALID_AMOUNT")

    def test_unapproved_lexical_forms_are_rejected(self):
        for value in ("1e3", "4_000", " 4000", "4000 ", ".50", "5000.",
                      "4999.995", "4.000,00", "４０００", "١٢", "NaN", "Infinity", "", "--1", "4000\n", "4000\r\n"):
            with self.subTest(value=value):
                self.assertEqual((routing.assess(value).route, routing.assess(value).reason),
                                 ("REJECTED", "INVALID_AMOUNT"))

    def test_length_limit_counts_sign_and_point(self):
        self.assertEqual(routing.assess("1" * 32).route, "HUMAN_REVIEW")
        for value in ("1" * 33, "+" + "1" * 32, "1" * 31 + ".0"):
            with self.subTest(value=value):
                self.assertEqual(routing.assess(value).route, "REJECTED")

    def test_non_string_is_a_caller_error(self):
        for value in (None, 1, 1.0, object()):
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(TypeError): routing.assess(value)
