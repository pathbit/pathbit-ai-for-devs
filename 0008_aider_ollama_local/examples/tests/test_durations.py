import unittest

from src.durations import total_minutes


class DurationTests(unittest.TestCase):
    def test_converts_hours_and_minutes(self):
        self.assertEqual(total_minutes(1, 15), 75)
