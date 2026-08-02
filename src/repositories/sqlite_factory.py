from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

from src.repositories.sqlite_repository import (
    AssetSQLiteRepository,
    DatabaseError,
    FinancialProfileSQLiteRepository,
    GoalSQLiteRepository,
    InvestmentSQLiteRepository,
    LiabilitySQLiteRepository,
    SQLiteDB,
)


def create_sqlite_repositories(db_path: str | Path | None = None) -> tuple:
    """Create SQLite-backed repository instances.

    If db_path is None, will read LAKSHMI_DB_PATH from environment.
    """
    path = db_path or os.environ.get("LAKSHMI_DB_PATH") or "data/lakshmi.db"
    db = SQLiteDB(path)
    # initialize done in constructor of repository base
    asset_repo = AssetSQLiteRepository(db)
    liability_repo = LiabilitySQLiteRepository(db)
    investment_repo = InvestmentSQLiteRepository(db)
    goal_repo = GoalSQLiteRepository(db)
    profile_repo = FinancialProfileSQLiteRepository(db)
    return asset_repo, liability_repo, investment_repo, goal_repo, profile_repo
