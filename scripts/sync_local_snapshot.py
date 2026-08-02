from pathlib import Path
import os
import json

ROOT = Path(__file__).resolve().parents[1]

from src.connectors.local_snapshot import LocalSnapshotConnector
from src.repositories.sqlite_factory import create_sqlite_repositories
from src.services.portfolio_sync_service import PortfolioSyncService


def main():
    sample_path = ROOT / "data" / "connectors" / "local_snapshot.json"
    connector = LocalSnapshotConnector(sample_path)

    db_path = os.environ.get("LAKSHMI_DB_PATH") or "data/lakshmi.db"
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(db_path)
    # create sync service and run
    service = PortfolioSyncService(connector, investment_repo._db, asset_repo, investment_repo)
    result = service.sync()

    print("Portfolio Sync")
    print("-" * 40)
    print(f"Source: {result.connector}")
    print(f"Status: {result.status}")
    print(f"Received: {result.received}")
    print(f"Added: {result.added}")
    print(f"Updated: {result.updated}")
    print(f"Removed: {result.removed}")
    if result.errors:
        print("Errors:")
        for e in result.errors:
            print(f" - {e}")


if __name__ == "__main__":
    main()
