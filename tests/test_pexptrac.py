from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from pexptrac.cli import main
from pexptrac.reports import build_report, filter_expenses, period_bounds
from pexptrac.store import ExpenseStore


class StoreTests(unittest.TestCase):
    def test_add_update_delete_expense(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ExpenseStore(Path(tmpdir) / "expenses.json")
            first = store.add(Decimal("10"), " Food ", date(2026, 5, 8), "Lunch")
            self.assertEqual(first.id, 1)
            self.assertEqual(first.amount, Decimal("10.00"))
            self.assertEqual(first.category, "food")

            updated = store.update(first.id, amount=Decimal("12.5"), category="groceries")
            self.assertEqual(updated.amount, Decimal("12.50"))
            self.assertEqual(updated.category, "groceries")

            deleted = store.delete(first.id)
            self.assertEqual(deleted.id, first.id)
            self.assertEqual(store.list_all(), [])

    def test_rejects_invalid_amount_and_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ExpenseStore(Path(tmpdir) / "expenses.json")
            with self.assertRaises(ValueError):
                store.add(Decimal("0"), "food", date(2026, 5, 8))
            with self.assertRaises(ValueError):
                store.add(Decimal("1"), " ", date(2026, 5, 8))


class ReportTests(unittest.TestCase):
    def test_filters_and_builds_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ExpenseStore(Path(tmpdir) / "expenses.json")
            store.add(Decimal("10"), "food", date(2026, 5, 1))
            store.add(Decimal("20"), "transport", date(2026, 5, 2))
            store.add(Decimal("30"), "food", date(2026, 6, 1))

            expenses = store.list_all()
            selected = filter_expenses(expenses, start=date(2026, 5, 1), end=date(2026, 5, 31))
            self.assertEqual(len(selected), 2)

            report = build_report(expenses, date(2026, 5, 1), date(2026, 5, 31))
            self.assertEqual(report.total, Decimal("30.00"))
            self.assertEqual(report.by_category["food"], Decimal("10.00"))
            self.assertEqual(report.by_category["transport"], Decimal("20.00"))
            self.assertEqual(report.largest.amount, Decimal("20.00"))

    def test_period_bounds(self) -> None:
        week_start, week_end = period_bounds("week", today=date(2026, 5, 8))
        self.assertEqual(week_start, date(2026, 5, 4))
        self.assertEqual(week_end, date(2026, 5, 10))
        month_start, month_end = period_bounds("month", today=date(2026, 5, 8))
        self.assertEqual(month_start, date(2026, 5, 1))
        self.assertEqual(month_end, date(2026, 5, 31))


class CliTests(unittest.TestCase):
    def test_cli_add_list_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_path = os.environ.get("PEXPTRAC_DATA")
            os.environ["PEXPTRAC_DATA"] = str(Path(tmpdir) / "expenses.json")
            try:
                self.assertEqual(main(["add", "7.25", "coffee", "--date", "2026-05-08"]), 0)
                self.assertEqual(main(["list", "--from", "2026-05-01", "--to", "2026-05-31"]), 0)
                self.assertEqual(main(["report", "--from", "2026-05-01", "--to", "2026-05-31"]), 0)
            finally:
                if old_path is None:
                    os.environ.pop("PEXPTRAC_DATA", None)
                else:
                    os.environ["PEXPTRAC_DATA"] = old_path


if __name__ == "__main__":
    unittest.main()
