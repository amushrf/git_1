from __future__ import annotations

import json
import os
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import Expense


class ExpenseStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_data_path()

    def list_all(self) -> list[Expense]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        return [Expense.from_dict(item) for item in raw.get("expenses", [])]

    def add(self, amount: Decimal, category: str, expense_date: date, note: str = "") -> Expense:
        expenses = self.list_all()
        expense = Expense(
            id=next_id(expenses),
            amount=normalize_amount(amount),
            category=normalize_category(category),
            date=expense_date,
            note=note.strip(),
        )
        expenses.append(expense)
        self.save(expenses)
        return expense

    def update(
        self,
        expense_id: int,
        amount: Decimal | None = None,
        category: str | None = None,
        expense_date: date | None = None,
        note: str | None = None,
    ) -> Expense:
        expenses = self.list_all()
        for index, expense in enumerate(expenses):
            if expense.id == expense_id:
                updated = Expense(
                    id=expense.id,
                    amount=normalize_amount(amount) if amount is not None else expense.amount,
                    category=normalize_category(category) if category is not None else expense.category,
                    date=expense_date or expense.date,
                    note=note.strip() if note is not None else expense.note,
                )
                expenses[index] = updated
                self.save(expenses)
                return updated
        raise KeyError(f"Expense {expense_id} was not found")

    def delete(self, expense_id: int) -> Expense:
        expenses = self.list_all()
        remaining = [expense for expense in expenses if expense.id != expense_id]
        if len(remaining) == len(expenses):
            raise KeyError(f"Expense {expense_id} was not found")
        deleted = next(expense for expense in expenses if expense.id == expense_id)
        self.save(remaining)
        return deleted

    def save(self, expenses: list[Expense]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"expenses": [expense.to_dict() for expense in sorted(expenses, key=lambda item: item.id)]}
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")


def default_data_path() -> Path:
    override = os.environ.get("PEXPTRAC_DATA")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".pexptrac" / "expenses.json"


def next_id(expenses: list[Expense]) -> int:
    return max((expense.id for expense in expenses), default=0) + 1


def normalize_amount(value: Decimal) -> Decimal:
    try:
        amount = Decimal(value).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Amount must be a valid number") from exc
    if amount <= 0:
        raise ValueError("Amount must be greater than zero")
    return amount


def normalize_category(value: str) -> str:
    category = value.strip().lower()
    if not category:
        raise ValueError("Category is required")
    return category
