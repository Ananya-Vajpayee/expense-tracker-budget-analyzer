"""Pure functions that analyse lists of Expense objects."""
import calendar
from collections import defaultdict
from datetime import date
from typing import Optional


def total_spent(expenses) -> float:
    return round(sum(e.amount for e in expenses), 2)


def category_totals(expenses) -> dict:
    totals = defaultdict(float)
    for e in expenses:
        totals[e.category] += e.amount
    return {k: round(v, 2) for k, v in totals.items()}


def monthly_totals(expenses) -> dict:
    totals = defaultdict(float)
    for e in expenses:
        totals[e.date[:7]] += e.amount
    return {k: round(v, 2) for k, v in sorted(totals.items())}


def top_categories(expenses, n: int = 3) -> list:
    totals = category_totals(expenses)
    return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:n]


def largest_expense(expenses):
    return max(expenses, key=lambda e: e.amount, default=None)


def forecast_month_end(expenses, month: str, today: Optional[date] = None) -> float:
    """Project month-end spend from the daily average so far.

    For past months returns the actual total; for the current month
    extrapolates: spent / days_elapsed * days_in_month.
    """
    today = today or date.today()
    year, mon = map(int, month.split("-"))
    days_in_month = calendar.monthrange(year, mon)[1]
    spent = total_spent(expenses)
    if (year, mon) < (today.year, today.month):
        return spent
    if (year, mon) > (today.year, today.month):
        return 0.0
    return round(spent / today.day * days_in_month, 2)
