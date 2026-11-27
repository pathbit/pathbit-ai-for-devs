import unittest
from datetime import date

from src.reports import daily_filename, hourly_filename


class ReportNameTests(unittest.TestCase):
    def test_daily_name_has_no_hour(self):
        self.assertEqual(daily_filename(date(2026, 6, 7)), "orders-2026-06-07.csv")

    def test_hourly_name_pads_the_hour(self):
        self.assertEqual(hourly_filename(date(2026, 6, 7), 2), "orders-2026-06-07-02.csv")
