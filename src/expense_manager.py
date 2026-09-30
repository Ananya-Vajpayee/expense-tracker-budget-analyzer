"""CRUD operations for expenses."""
import logging
from typing import Optional

from src.models import Expense
from src.storage import DataStore
from src.validators import (validate_amount, validate_category, validate_date,
                            validate_month)

log = logging.getLogger(__name__)


class NotFoundError(LookupError):
    """Raised when an expense id does not exist."""


class ExpenseManager:
    def __init__(self, store: DataStore):
        self.store = store

    def add(self, amount, category, description="", date=None) -> Expense:
        expense = Expense(
            id=self.store.next_id(),
            amount=validate_amount(amount),
            category=validate_category(category),
            description=str(description or "").strip(),
            date=validate_date(date),
        )
        self.store.expenses.append(expense)
        self.store.save()
        log.info("Added expense id=%d amount=%.2f", expense.id, expense.amount)
        return expense

    def get(self, expense_id: int) -> Expense:
        for e in self.store.expenses:
            if e.id == int(expense_id):
                return e
        raise NotFoundError(f"No expense with id {expense_id}")

    def list(self, month: Optional[str] = None, category: Optional[str] = None) -> list:
        items = self.store.expenses
        if month:
            month = validate_month(month)
            items = [e for e in items if e.date.startswith(month)]
        if category:
            category = validate_category(category)
            items = [e for e in items if e.category == category]
        return sorted(items, key=lambda e: (e.date, e.id))

    def update(self, expense_id: int, **fields) -> Expense:
        expense = self.get(expense_id)
        if fields.get("amount") is not None:
            expense.amount = validate_amount(fields["amount"])
        if fields.get("category") is not None:
            expense.category = validate_category(fields["category"])
        if fields.get("description") is not None:
            expense.description = str(fields["description"]).strip()
        if fields.get("date") is not None:
            expense.date = validate_date(fields["date"])
        self.store.save()
        log.info("Updated expense id=%d", expense.id)
        return expense

    def delete(self, expense_id: int) -> Expense:
        expense = self.get(expense_id)
        self.store.expenses.remove(expense)
        self.store.save()
        log.info("Deleted expense id=%d", expense.id)
        return expense
