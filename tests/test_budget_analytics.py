import os
import tempfile
import unittest
from datetime import date

from src.analytics import (category_totals, forecast_month_end, monthly_totals,
                           top_categories, total_spent)
from src.budget import BudgetManager
from src.expense_manager import ExpenseManager
from src.storage import DataStore


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = DataStore(os.path.join(self.tmp.name, "d.json"))
        self.em = ExpenseManager(self.store)
        self.bm = BudgetManager(self.store)
        self.em.add(100, "food", date="2026-09-01")
        self.em.add(50, "food", date="2026-09-10")
        self.em.add(30, "bills", date="2026-08-05")

    def tearDown(self):
        self.tmp.cleanup()

    def test_totals(self):
        items = self.em.list()
        self.assertEqual(total_spent(items), 180.0)
        self.assertEqual(category_totals(items), {"Food": 150.0, "Bills": 30.0})
        self.assertEqual(monthly_totals(items), {"2026-08": 30.0, "2026-09": 150.0})
        self.assertEqual(top_categories(items, 1)[0][0], "Food")

    def test_forecast(self):
        sept = self.em.list(month="2026-09")
        self.assertEqual(forecast_month_end(sept, "2026-09", date(2026, 9, 15)), 300.0)
        self.assertEqual(forecast_month_end(sept, "2026-09", date(2026, 10, 2)), 150.0)

    def test_budget_states(self):
        self.bm.set_budget("food", 180)
        self.assertEqual(self.bm.status("2026-09")[0]["state"], "WARNING")
        self.bm.set_budget("food", 100)
        self.assertEqual(self.bm.status("2026-09")[0]["state"], "EXCEEDED")
        self.bm.set_budget("food", 1000)
        self.assertEqual(self.bm.status("2026-09")[0]["state"], "OK")


if __name__ == "__main__":
    unittest.main()
