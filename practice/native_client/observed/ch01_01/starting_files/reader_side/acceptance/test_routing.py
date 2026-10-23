"""Independent acceptance cases. In the lab, keep this directory outside agent write scope."""
import unittest
from treasury.routing import assess

class RoutingAcceptance(unittest.TestCase):
    def check(self, raw, route, reason):
        result = assess(raw)
        self.assertEqual((result.route, result.reason, result.policy_version),
                         (route, reason, "BR-001/v1"))

    def test_positive_below_limit(self):
        self.check("4000.00", "STANDARD_QUEUE", "BELOW_LIMIT")

    def test_exact_boundary_requires_review(self):
        self.check("5000.00", "HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT")

    def test_above_boundary_requires_review(self):
        self.check("5001.00", "HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT")

    def test_negative_amount_rejected(self):
        self.check("-0.01", "REJECTED", "INVALID_AMOUNT")

    def test_zero_amount_rejected(self):
        self.check("0.00", "REJECTED", "INVALID_AMOUNT")

    def test_nonnumeric_amount_rejected(self):
        self.check("not-an-amount", "REJECTED", "INVALID_AMOUNT")

    def test_nonfinite_amount_rejected(self):
        self.check("NaN", "REJECTED", "INVALID_AMOUNT")

if __name__ == "__main__":
    unittest.main()
