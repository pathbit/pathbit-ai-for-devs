import unittest

from src.pricing import shipping_cents


class ShippingTests(unittest.TestCase):
    def test_standard_shipping(self):
        self.assertEqual(shipping_cents(5_000), 750)
