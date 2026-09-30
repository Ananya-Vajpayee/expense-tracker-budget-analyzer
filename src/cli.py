"""Command-line interface: argparse subcommands + interactive menu."""
import argparse
import logging

from src.budget import BudgetManager
from src.expense_manager import ExpenseManager, NotFoundError
from src.report import export_csv, monthly_report
from src.storage import DataStore
from src.validators import ValidationError, validate_month

log = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="expense-tracker",
                                description="Expense Tracker & Budget Analyzer")
    p.add_argument("--data", default="data/expenses.json", help="path to data file")
    sub = p.add_subparsers(dest="command")

    a = sub.add_parser("add", help="add an expense")
    a.add_argument("--amount", required=True)
    a.add_argument("--category", required=True)
    a.add_argument("--desc", default="")
    a.add_argument("--date", help="YYYY-MM-DD (default today)")

    l = sub.add_parser("list", help="list expenses")
    l.add_argument("--month", help="YYYY-MM")
    l.add_argument("--category")

    e = sub.add_parser("edit", help="edit an expense")
    e.add_argument("id", type=int)
    e.add_argument("--amount")
    e.add_argument("--category")
    e.add_argument("--desc")
    e.add_argument("--date")

    d = sub.add_parser("delete", help="delete an expense")
    d.add_argument("id", type=int)

    b = sub.add_parser("budget", help="set or view budgets")
    b.add_argument("action", choices=["set", "status", "remove"])
    b.add_argument("category", nargs="?")
    b.add_argument("limit", nargs="?")
    b.add_argument("--month", help="YYYY-MM (status only)")

    s = sub.add_parser("summary", help="monthly analytics report")
    s.add_argument("--month", help="YYYY-MM")

    x = sub.add_parser("export", help="export expenses to CSV")
    x.add_argument("path")
    x.add_argument("--month", help="YYYY-MM")

    sub.add_parser("menu", help="interactive menu")
    return p


def print_expenses(items) -> None:
    if not items:
        print("No expenses found.")
        return
    print(f"{'ID':<4} {'Date':<11} {'Category':<15} {'Amount':>10}  Description")
    for x in items:
        print(f"{x.id:<4} {x.date:<11} {x.category:<15} {x.amount:>10.2f}  {x.description}")


def print_budget(rows) -> None:
    if not rows:
        print("No budgets set.")
        return
    for r in rows:
        print(f"{r['category']:<15} spent {r['spent']:>9.2f} of {r['limit']:<9.2f}"
              f" ({r['percent']:.1f}%) remaining {r['remaining']:.2f} [{r['state']}]")


def dispatch(args, em: ExpenseManager, bm: BudgetManager) -> None:
    cmd = args.command
    if cmd == "add":
        x = em.add(args.amount, args.category, args.desc, args.date)
        print(f"Added expense #{x.id}: {x.amount:.2f} on {x.category} ({x.date})")
        for r in bm.status(x.date[:7]):
            if r["category"] == x.category and r["state"] != "OK":
                print(f"!! Budget {r['state']} for {x.category}: {r['percent']}% used")
    elif cmd == "list":
        print_expenses(em.list(args.month, args.category))
    elif cmd == "edit":
        x = em.update(args.id, amount=args.amount, category=args.category,
                      description=args.desc, date=args.date)
        print(f"Updated expense #{x.id}")
    elif cmd == "delete":
        em.delete(args.id)
        print(f"Deleted expense #{args.id}")
    elif cmd == "budget":
        if args.action == "set":
            if not args.category or not args.limit:
                raise ValidationError("Usage: budget set <category> <limit>")
            cat, lim = bm.set_budget(args.category, args.limit)
            print(f"Budget for {cat} set to {lim:.2f}")
        elif args.action == "remove":
            bm.remove_budget(args.category)
            print("Budget removed")
        else:
            print_budget(bm.status(args.month))
    elif cmd == "summary":
        month = validate_month(args.month)
        print(monthly_report(month, em.list(month), bm.status(month)))
    elif cmd == "export":
        items = em.list(args.month)
        print(f"Exported {export_csv(items, args.path)} rows to {args.path}")


def interactive_menu(em: ExpenseManager, bm: BudgetManager) -> None:
    menu = ("\n1) Add expense  2) List expenses  3) Delete expense\n"
            "4) Set budget    5) Budget status  6) Monthly summary\n"
            "7) Export CSV    0) Quit")
    while True:
        print(menu)
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                args = argparse.Namespace(command="add", amount=input("Amount: "),
                                          category=input("Category: "),
                                          desc=input("Description: "),
                                          date=input("Date (YYYY-MM-DD, blank=today): "))
            elif choice == "2":
                args = argparse.Namespace(command="list", month=input("Month (blank=all): ") or None,
                                          category=None)
            elif choice == "3":
                args = argparse.Namespace(command="delete", id=int(input("ID: ")))
            elif choice == "4":
                args = argparse.Namespace(command="budget", action="set",
                                          category=input("Category: "), limit=input("Limit: "),
                                          month=None)
            elif choice == "5":
                args = argparse.Namespace(command="budget", action="status", category=None,
                                          limit=None, month=input("Month (blank=current): ") or None)
            elif choice == "6":
                args = argparse.Namespace(command="summary", month=input("Month (blank=current): ") or None)
            elif choice == "7":
                args = argparse.Namespace(command="export", path=input("File path: "), month=None)
            elif choice == "0":
                print("Goodbye!")
                return
            else:
                print("Invalid choice.")
                continue
            dispatch(args, em, bm)
        except (ValidationError, NotFoundError, KeyError, ValueError) as exc:
            print(f"Error: {exc}")


def run(argv=None) -> int:
    args = build_parser().parse_args(argv)
    store = DataStore(args.data)
    em, bm = ExpenseManager(store), BudgetManager(store)
    try:
        if args.command in (None, "menu"):
            interactive_menu(em, bm)
        else:
            dispatch(args, em, bm)
        return 0
    except (ValidationError, NotFoundError, KeyError) as exc:
        log.warning("User error: %s", exc)
        print(f"Error: {exc}")
        return 1
    except OSError as exc:
        log.error("I/O failure: %s", exc)
        print(f"File error: {exc}")
        return 2
