# pExpTrac

pExpTrac is a small command-line personal expense tracker. It records expenses in a local JSON file, lists them by date range, edits or deletes entries, and prints spending reports.

## Requirements

- Python 3.10 or newer

## Quick Start

```bash
python -m pexptrac --help
python -m pexptrac add 12.50 food --note "Lunch"
python -m pexptrac list
python -m pexptrac report --period month
```

By default, pExpTrac stores data at `~/.pexptrac/expenses.json`.
For testing or a separate data file, set `PEXPTRAC_DATA`:

```bash
PEXPTRAC_DATA=./expenses.json python -m pexptrac add 42.00 transport --date 2026-05-08
```

## Commands

### Add an Expense

```bash
python -m pexptrac add AMOUNT CATEGORY --date YYYY-MM-DD --note "optional note"
```

### List Expenses

```bash
python -m pexptrac list
python -m pexptrac list --from 2026-05-01 --to 2026-05-31 --category food
```

### Edit an Expense

```bash
python -m pexptrac edit EXPENSE_ID --amount 15 --category groceries --note "Updated"
```

### Delete an Expense

```bash
python -m pexptrac delete EXPENSE_ID
```

### Reports

```bash
python -m pexptrac report --period week
python -m pexptrac report --period month
python -m pexptrac report --from 2026-05-01 --to 2026-05-31
```

Reports include total spending, totals by category, and the largest expense in the selected period.

## Run Tests

```bash
python -m unittest discover -s tests
```
