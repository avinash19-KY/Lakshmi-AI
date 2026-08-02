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
The next goal-aware check compares each goal's required monthly saving with the
current monthly surplus.
Before a specific investment is considered, the decision-readiness gate checks
whether reserves, cash flow, and goal funding conditions support evaluation.
The first local chat layer is available with `python -m src.chat` and answers
the core status, emergency-fund, and investment-readiness questions from the
same local data. It also surfaces the highest-priority focus area from
Portfolio Intelligence.
Financial Memory is opt-in: use `remember <note>` in the local chat to save a
decision to `data/decision_journal.json`, or ask to show the decision journal.
Ask for a “review”, “report”, or “morning update” to receive a concise local
financial briefing.

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

## Persistence (SQLite)

SQLite persistence is available as an optional, local-only data store. By default
the application continues to use in-memory repositories and the `data/` import
files. To enable persistence:

1. Set the LAKSHMI_DB_PATH environment variable to the desired database file.
   Example (Unix/macOS):

```bash
export LAKSHMI_DB_PATH=data/lakshmi.db
python -m src.main
```

2. Running the demo import pipeline with the environment variable set will
   persist imported data into the configured SQLite database:

```bash
export LAKSHMI_DB_PATH=data/lakshmi.db
python scripts/demo_import_pipeline.py
```

Notes:
- The database is created and initialized automatically if it does not exist.
- Imports use a replace-all strategy for each entity: the repositories are
  cleared and new rows are inserted when `ProfileService.load_data()` runs.
- The database file is local-only and ignored by git (see `.gitignore`).

## Portfolio Synchronization (Read-only connectors)

Lakshmi AI can ingest read-only portfolio snapshots from external sources via a
small connector/synchronization abstraction. This layer is intentionally
provider-agnostic and strictly read-only: connectors may only fetch data — they
cannot place orders or modify external accounts.

Key points:
- Connector interface: `PortfolioConnector.fetch_holdings()` returns canonical
  holding records used by the sync service.
- Local snapshot connector: a simple `LocalSnapshotConnector` reads JSON
  snapshots from `data/connectors/` and is provided as an example adapter.
- Synchronization service: `PortfolioSyncService` maps connector holdings to the
  existing domain models and persists them via repository interfaces.
- Provenance and ownership: synchronized records are tracked in the
  `connector_mappings` SQLite table so connector-managed records are
  distinguishable from manually-created records. Connector sync never deletes
  manual records.
- Idempotency and reconciliation: repeated syncs are idempotent. Updates to
  holdings update existing connector-managed records. If a previously-mapped
  holding is absent from a full snapshot, the connector-managed record is
  removed.

Running the example local connector sync (uses `data/connectors/local_snapshot.json`):

```bash
# Persist the sync results to a local DB (recommended)
export LAKSHMI_DB_PATH=data/lakshmi.db
python scripts/sync_local_snapshot.py
```

Alternatively supply a custom DB path:

```bash
export LAKSHMI_DB_PATH=/tmp/my_lakshmi.db
python scripts/sync_local_snapshot.py
```

Difference from imports:
- Imports (`data/*.csv` or `data/*.xlsx`) are user-provided dataset ingestion.
- Synchronization is for externally-managed portfolios (connectors) and tracks
  ownership so manual records are preserved.

Privacy & security:
- Connectors are read-only. No trading or external writes are possible.
- Credentials (if added later) must never be committed or stored in the DB.
- The local SQLite DB remains on your machine and is ignored by Git.

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

To persist the demo import results to SQLite:

```bash
export LAKSHMI_DB_PATH=data/lakshmi.db
python scripts/demo_import_pipeline.py
```

## Portfolio Intelligence

The next phase is a rule-based focus layer that highlights the weakest part of
the current financial picture and explains why it deserves attention.

## Investment Research Foundation & Deterministic Scenario Engine

A lightweight research abstraction and deterministic scenario engine are available in this codebase for Phase 4.

- ResearchProvider abstraction: `src.research.provider.ResearchProvider`
- ResearchSnapshot: `src.research.provider.ResearchSnapshot` (includes instrument id, as-of date and source provenance)
- LocalResearchProvider: deterministic local JSON provider `src.research.local_provider.LocalResearchProvider`

Scenario Engine highlights (deterministic, reproducible, auditable):

- Lump-sum growth projection
- Recurring contribution (SIP) projection with optional annual step-up
- Goal funding projection (uses existing goal rules where appropriate)
- Deterministic portfolio shock (category-level shocks)
- Allocation change simulation
- Debt vs Investment deterministic comparison
- Structured scenario comparison output

Important design rules:

- Facts (research snapshots) are separate from Assumptions (scenario inputs).
- Scenarios are deterministic and do not mutate the portfolio or database.
- No live market data, no Monte Carlo, no AI-driven calculations in V1.

See `src/research` and `src/scenarios` for implementation and `tests/test_research_and_scenarios.py` for example usage.

## Run tests

```bash
python -m pytest
```
