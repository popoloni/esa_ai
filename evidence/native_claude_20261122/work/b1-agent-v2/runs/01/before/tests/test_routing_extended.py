"""Five protected public-API diagnostics added to the unchanged seven historical cases."""
import unittest
from treasury import routing


class RoutingExtended(unittest.TestCase):
    def assert_rejected(self, amount):
        result = routing.assess(amount)
        self.assertEqual((result.route, result.reason, result.policy_version),
                         ("REJECTED", "INVALID_AMOUNT", "BR-001/v1"))

    def test_positive_infinity_rejected(self):
        self.assert_rejected("Infinity")

    def test_negative_infinity_rejected(self):
        self.assert_rejected("-Infinity")

    def test_short_infinity_rejected(self):
        self.assert_rejected("inf")

    def test_signaling_nan_rejected(self):
        self.assert_rejected("sNaN")

    def test_non_string_argument_is_programming_error(self):
        for value in (None, 4000, 4000.0, object()):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaises(TypeError):
                    routing.assess(value)
