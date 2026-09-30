"""Input validation helpers. All raise ValidationError on bad input."""
import math
from datetime import date, datetime


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_amount(value) -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Amount must be a number, got {value!r}")
    if math.isnan(amount) or math.isinf(amount) or amount <= 0:
        raise ValidationError("Amount must be a positive, finite number")
    return round(amount, 2)


def validate_date(value=None) -> str:
    """Return an ISO date string; defaults to today when value is empty."""
    if not value:
        return date.today().isoformat()
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise ValidationError("Date must be in YYYY-MM-DD format")


def validate_category(value) -> str:
    if value is None or not str(value).strip():
        raise ValidationError("Category cannot be empty")
    category = str(value).strip().title()
    if len(category) > 30:
        raise ValidationError("Category must be 30 characters or fewer")
    return category


def validate_month(value=None) -> str:
    """Return 'YYYY-MM'; defaults to the current month."""
    if not value:
        return date.today().strftime("%Y-%m")
    try:
        return datetime.strptime(str(value), "%Y-%m").strftime("%Y-%m")
    except ValueError:
        raise ValidationError("Month must be in YYYY-MM format")
