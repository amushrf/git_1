from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal, InvalidOperation

from .reports import build_report, filter_expenses, period_bounds
from .store import ExpenseStore


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = ExpenseStore()
    try:
        return args.handler(args, store)
    except (KeyError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pExpTrac", description="Personal expense tracker CLI")
    subcommands = parser.add_subparsers(required=True)

    add_parser = subcommands.add_parser("add", help="add an expense")
    add_parser.add_argument("amount", type=parse_amount)
    add_parser.add_argument("category")
    add_parser.add_argument("--date", type=parse_date, default=date.today())
    add_parser.add_argument("--note", default="")
    add_parser.set_defaults(handler=handle_add)

    list_parser = subcommands.add_parser("list", help="list expenses")
    list_parser.add_argument("--from", dest="start", type=parse_date)
    list_parser.add_argument("--to", dest="end", type=parse_date)
    list_parser.add_argument("--category")
    list_parser.set_defaults(handler=handle_list)

    edit_parser = subcommands.add_parser("edit", help="edit an expense")
    edit_parser.add_argument("expense_id", type=int)
    edit_parser.add_argument("--amount", type=parse_amount)
    edit_parser.add_argument("--category")
    edit_parser.add_argument("--date", dest="expense_date", type=parse_date)
    edit_parser.add_argument("--note")
    edit_parser.set_defaults(handler=handle_edit)

    delete_parser = subcommands.add_parser("delete", help="delete an expense")
    delete_parser.add_argument("expense_id", type=int)
    delete_parser.set_defaults(handler=handle_delete)

    report_parser = subcommands.add_parser("report", help="show a spending report")
    report_parser.add_argument("--period", choices=["week", "month"])
    report_parser.add_argument("--from", dest="start", type=parse_date)
    report_parser.add_argument("--to", dest="end", type=parse_date)
    report_parser.set_defaults(handler=handle_report)
    return parser


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must use YYYY-MM-DD") from exc


def parse_amount(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("Amount must be a valid number") from exc


def handle_add(args: argparse.Namespace, store: ExpenseStore) -> int:
    expense = store.add(args.amount, args.category, args.date, args.note)
    print(f"Added #{expense.id}: {format_money(expense.amount)} {expense.category} on {expense.date}")
    return 0


def handle_list(args: argparse.Namespace, store: ExpenseStore) -> int:
    expenses = filter_expenses(store.list_all(), start=args.start, end=args.end, category=args.category)
    if not expenses:
        print("No expenses found.")
        return 0
    for expense in expenses:
        note = f" - {expense.note}" if expense.note else ""
        print(f"#{expense.id} {expense.date} {format_money(expense.amount)} {expense.category}{note}")
    return 0


def handle_edit(args: argparse.Namespace, store: ExpenseStore) -> int:
    if args.amount is None and args.category is None and args.expense_date is None and args.note is None:
        raise ValueError("Provide at least one field to update")
    expense = store.update(
        args.expense_id,
        amount=args.amount,
        category=args.category,
        expense_date=args.expense_date,
        note=args.note,
    )
    print(f"Updated #{expense.id}: {format_money(expense.amount)} {expense.category} on {expense.date}")
    return 0


def handle_delete(args: argparse.Namespace, store: ExpenseStore) -> int:
    expense = store.delete(args.expense_id)
    print(f"Deleted #{expense.id}: {format_money(expense.amount)} {expense.category} on {expense.date}")
    return 0


def handle_report(args: argparse.Namespace, store: ExpenseStore) -> int:
    if args.period:
        start, end = period_bounds(args.period)
    else:
        start = args.start or date.today().replace(day=1)
        end = args.end or date.today()
    if start > end:
        raise ValueError("Start date must be before or equal to end date")

    report = build_report(store.list_all(), start, end)
    print(f"Report: {report.start} to {report.end}")
    print(f"Expenses: {report.count}")
    print(f"Total: {format_money(report.total)}")
    print("By category:")
    if report.by_category:
        for category, total in report.by_category.items():
            print(f"  {category}: {format_money(total)}")
    else:
        print("  none")
    if report.largest:
        print(
            "Largest: "
            f"#{report.largest.id} {format_money(report.largest.amount)} "
            f"{report.largest.category} on {report.largest.date}"
        )
    else:
        print("Largest: none")
    return 0


def format_money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))}"
