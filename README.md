# Lakshmi AI

Lakshmi AI is a local-first, personal financial decision-support tool.

## Current capability

The application shows a starter financial profile and calculates total assets,
total liabilities, net worth, monthly surplus, savings rate, and emergency-fund
coverage from structured financial data. It also tracks a goal and shows simple
full-value funding scenarios without assuming investment returns, plus the
current allocation of recorded assets by category. A transparent financial
health score summarizes emergency reserves, savings capacity, and net worth.

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

## Run tests

```bash
python -m pytest
```
