import unittest
from src.validators import (ValidationError, validate_amount, validate_category,
                            validate_date, validate_month)


class TestValidators(unittest.TestCase):
    def test_amount_valid(self):
        self.assertEqual(validate_amount("12.345"), 12.35)

    def test_amount_invalid(self):
        for bad in ["abc", -5, 0, "nan", "inf", None]:
            with self.assertRaises(ValidationError):
                validate_amount(bad)

    def test_date(self):
        self.assertEqual(validate_date("2026-01-31"), "2026-01-31")
        with self.assertRaises(ValidationError):
            validate_date("31-01-2026")
        with self.assertRaises(ValidationError):
            validate_date("2026-02-30")

    def test_category(self):
        self.assertEqual(validate_category("  food "), "Food")
        with self.assertRaises(ValidationError):
            validate_category("   ")
        with self.assertRaises(ValidationError):
            validate_category("x" * 31)

    def test_month(self):
        self.assertEqual(validate_month("2026-09"), "2026-09")
        with self.assertRaises(ValidationError):
            validate_month("2026-13")


if __name__ == "__main__":
    unittest.main()
