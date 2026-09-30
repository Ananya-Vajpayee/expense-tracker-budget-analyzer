"""JSON persistence layer shared by all managers."""
import json
import logging
import os
from pathlib import Path

from src.models import Expense

log = logging.getLogger(__name__)


class DataStore:
    """Holds expenses and budgets in memory and persists them to JSON."""

    def __init__(self, path: str = "data/expenses.json"):
        self.path = Path(path)
        self.expenses: list = []
        self.budgets: dict = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            log.info("No data file at %s; starting fresh", self.path)
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.expenses = [Expense.from_dict(e) for e in raw.get("expenses", [])]
            self.budgets = {k: float(v) for k, v in raw.get("budgets", {}).items()}
            log.info("Loaded %d expenses", len(self.expenses))
        except (json.JSONDecodeError, KeyError, ValueError, OSError) as exc:
            backup = self.path.with_suffix(".corrupt")
            log.error("Corrupt data file (%s); backing up to %s", exc, backup)
            try:
                os.replace(self.path, backup)
            except OSError:
                pass
            self.expenses, self.budgets = [], {}

    def save(self) -> None:
        """Atomic write: write to temp file, then replace."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        payload = {
            "expenses": [e.to_dict() for e in self.expenses],
            "budgets": self.budgets,
        }
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)

    def next_id(self) -> int:
        return max((e.id for e in self.expenses), default=0) + 1
