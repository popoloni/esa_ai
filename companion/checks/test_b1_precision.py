"""Public counterexamples within B1-API/v1; not reused as v2 inputs."""
import unittest
from treasury import routing
class ExactValue(unittest.TestCase):
    def test_positive_value_below_boundary_is_not_rounded_up(self):
        r = routing.assess("4999.9999999999999")
        self.assertEqual((r.route, r.reason), ("STANDARD_QUEUE", "BELOW_LIMIT"))
    def test_positive_tiny_value_is_not_rounded_to_zero(self):
        r = routing.assess("1e-400")
        self.assertEqual((r.route, r.reason), ("STANDARD_QUEUE", "BELOW_LIMIT"))
