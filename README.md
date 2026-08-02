# Lakshmi AI

Lakshmi AI is a local-first, personal financial decision-support tool.

## Current capability

The application shows a starter financial profile and calculates total assets,
total liabilities, net worth, monthly surplus, savings rate, and emergency-fund
coverage from structured financial data. It also tracks a goal and shows simple
full-value funding scenarios without assuming investment returns, plus the
current allocation of recorded assets by category. A transparent financial
health score summarizes emergency reserves, savings capacity, and net worth.
It also shows the emergency-fund target amount and the remaining gap to that
target.
The newest phase adds rule-based Portfolio Intelligence so Lakshmi AI can point
to the weakest part of the financial picture and suggest the next area to focus
on. It also applies a conservative investment guardrail: positive monthly
surplus is not treated as risk capital until the emergency-fund target is met.

## Update your data

Edit the files in `data/` to update the financial snapshot without changing
Python code:

- `profile.csv` — income, expenses, and emergency fund
- `assets.csv` — assets such as cash, funds, and EPF
- `liabilities.csv` — loans or other amounts owed
- `goals.csv` — financial goals and their current allocation

## Run locally

```bash
python -m src.main
```

## Demo the import pipeline

The repository includes sample import files in `data/import_examples/` for both CSV and Excel formats:

- `profile.csv` / `profile.xlsx`
- `assets.csv` / `assets.xlsx`
- `liabilities.csv` / `liabilities.xlsx`
- `investments.csv` / `investments.xlsx`
- `goals.csv` / `goals.xlsx`

Run the demo script to import these files, populate repositories, and print the same financial health report:

```bash
python scripts/demo_import_pipeline.py
```

## Portfolio Intelligence

The next phase is a rule-based focus layer that highlights the weakest part of
the current financial picture and explains why it deserves attention.

## Run tests

```bash
python -m pytest
```
