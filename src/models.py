"""Data model for a single expense record."""
from dataclasses import dataclass, asdict


@dataclass
class Expense:
    id: int
    amount: float
    category: str
    description: str
    date: str  # ISO format: YYYY-MM-DD

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        return cls(
            id=int(data["id"]),
            amount=float(data["amount"]),
            category=str(data["category"]),
            description=str(data.get("description", "")),
            date=str(data["date"]),
        )
