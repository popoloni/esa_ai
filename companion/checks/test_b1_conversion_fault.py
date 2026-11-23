"""Supplementary fault injection for the declared seam of supplied B1 packs.

This is not a universal learner acceptance test. The known candidates import
Decimal into their routing module; this controlled dependency failure tests
that exception boundary without dictating how other correct repairs parse.
"""
import unittest
from unittest.mock import patch
from treasury import routing


class ConversionFaultProbe(unittest.TestCase):
    def test_unexpected_conversion_failure_propagates(self):
        with patch.object(routing, "Decimal", side_effect=RuntimeError("injected conversion fault")):
            with self.assertRaisesRegex(RuntimeError, "injected conversion fault"):
                routing.assess("4000.00")
