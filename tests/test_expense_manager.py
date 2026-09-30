import os
import tempfile
import unittest

from src.expense_manager import ExpenseManager, NotFoundError
from src.storage import DataStore
from src.validators import ValidationError


class TestExpenseManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "d.json")
        self.em = ExpenseManager(DataStore(self.path))

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_and_persist(self):
        self.em.add(100, "food", "lunch", "2026-09-01")
        reloaded = ExpenseManager(DataStore(self.path))
        self.assertEqual(len(reloaded.list()), 1)
        self.assertEqual(reloaded.list()[0].category, "Food")

    def test_ids_increment(self):
        a = self.em.add(1, "a", date="2026-09-01")
        b = self.em.add(2, "a", date="2026-09-01")
        self.assertEqual(b.id, a.id + 1)

    def test_filters(self):
        self.em.add(10, "food", date="2026-08-01")
        self.em.add(20, "bills", date="2026-09-01")
        self.assertEqual(len(self.em.list(month="2026-09")), 1)
        self.assertEqual(len(self.em.list(category="Food")), 1)

    def test_update_delete(self):
        x = self.em.add(10, "food", date="2026-09-01")
        self.em.update(x.id, amount=25)
        self.assertEqual(self.em.get(x.id).amount, 25.0)
        self.em.delete(x.id)
        with self.assertRaises(NotFoundError):
            self.em.get(x.id)

    def test_invalid_add(self):
        with self.assertRaises(ValidationError):
            self.em.add(-1, "food")

    def test_corrupt_file_recovered(self):
        with open(self.path, "w") as f:
            f.write("{not json")
        store = DataStore(self.path)
        self.assertEqual(store.expenses, [])
        self.assertTrue(os.path.exists(self.path.replace(".json", ".corrupt")))


if __name__ == "__main__":
    unittest.main()
