"""Text report generation and CSV export."""
import csv
from pathlib import Path

from src.analytics import (category_totals, forecast_month_end,
                           largest_expense, total_spent)


def bar_chart(totals: dict, width: int = 30) -> str:
    if not totals:
        return "  (no data)"
    peak = max(totals.values())
    lines = []
    for cat, amt in sorted(totals.items(), key=lambda kv: -kv[1]):
        bar = "#" * max(1, int(amt / peak * width))
        lines.append(f"  {cat:<15} {bar} {amt:.2f}")
    return "\n".join(lines)


def monthly_report(month: str, expenses: list, budget_rows: list) -> str:
    out = [f"===== Report for {month} =====",
           f"Total spent      : {total_spent(expenses):.2f}",
           f"Transactions     : {len(expenses)}"]
    big = largest_expense(expenses)
    if big:
        out.append(f"Largest expense  : {big.amount:.2f} ({big.category}, {big.date})")
    out.append(f"Projected total  : {forecast_month_end(expenses, month):.2f}")
    out += ["", "Spending by category:", bar_chart(category_totals(expenses))]
    if budget_rows:
        out += ["", "Budget status:"]
        for r in budget_rows:
            out.append(f"  {r['category']:<15} {r['spent']:>9.2f} / {r['limit']:<9.2f}"
                       f" {r['percent']:>6.1f}%  [{r['state']}]")
    return "\n".join(out)


def export_csv(expenses: list, path: str) -> int:
    """Write expenses to CSV; returns number of rows written."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "category", "amount", "description"])
        for e in expenses:
            writer.writerow([e.id, e.date, e.category, f"{e.amount:.2f}", e.description])
    return len(expenses)
