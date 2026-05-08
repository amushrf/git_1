from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from .models import Expense


@dataclass(frozen=True)
class Report:
    start: date
    end: date
    total: Decimal
    by_category: dict[str, Decimal]
    largest: Expense | None
    count: int


def filter_expenses(
    expenses: list[Expense],
    start: date | None = None,
    end: date | None = None,
    category: str | None = None,
) -> list[Expense]:
    normalized_category = category.strip().lower() if category else None
    result = []
    for expense in expenses:
        if start and expense.date < start:
            continue
        if end and expense.date > end:
            continue
        if normalized_category and expense.category != normalized_category:
            continue
        result.append(expense)
    return sorted(result, key=lambda item: (item.date, item.id))


def period_bounds(period: str, today: date | None = None) -> tuple[date, date]:
    current = today or date.today()
    if period == "week":
        start = current - timedelta(days=current.weekday())
        return start, start + timedelta(days=6)
    if period == "month":
        start = current.replace(day=1)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1)
        else:
            next_month = start.replace(month=start.month + 1)
        return start, next_month - timedelta(days=1)
    raise ValueError("Period must be 'week' or 'month'")


def build_report(expenses: list[Expense], start: date, end: date) -> Report:
    selected = filter_expenses(expenses, start=start, end=end)
    by_category: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    total = Decimal("0.00")
    for expense in selected:
        total += expense.amount
        by_category[expense.category] += expense.amount
    largest = max(selected, key=lambda item: item.amount, default=None)
    return Report(
        start=start,
        end=end,
        total=total.quantize(Decimal("0.01")),
        by_category=dict(sorted(by_category.items())),
        largest=largest,
        count=len(selected),
    )
