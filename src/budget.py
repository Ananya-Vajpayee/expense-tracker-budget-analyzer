"""Budget limits per category and status checks."""
import logging

from src.analytics import category_totals
from src.storage import DataStore
from src.validators import validate_amount, validate_category, validate_month

log = logging.getLogger(__name__)

WARNING_THRESHOLD = 80.0  # percent of budget used


class BudgetManager:
    def __init__(self, store: DataStore):
        self.store = store

    def set_budget(self, category, limit) -> tuple:
        category = validate_category(category)
        limit = validate_amount(limit)
        self.store.budgets[category] = limit
        self.store.save()
        log.info("Budget set: %s = %.2f", category, limit)
        return category, limit

    def remove_budget(self, category) -> None:
        category = validate_category(category)
        if category not in self.store.budgets:
            raise KeyError(f"No budget set for {category}")
        del self.store.budgets[category]
        self.store.save()

    def status(self, month=None) -> list:
        """Return one status dict per budgeted category for the month."""
        month = validate_month(month)
        spent_by_cat = category_totals(
            [e for e in self.store.expenses if e.date.startswith(month)]
        )
        rows = []
        for category, limit in sorted(self.store.budgets.items()):
            spent = spent_by_cat.get(category, 0.0)
            percent = spent / limit * 100
            if spent > limit:
                state = "EXCEEDED"
            elif percent >= WARNING_THRESHOLD:
                state = "WARNING"
            else:
                state = "OK"
            rows.append({
                "category": category, "limit": limit, "spent": round(spent, 2),
                "remaining": round(limit - spent, 2),
                "percent": round(percent, 1), "state": state,
            })
        return rows
