import os
from tempfile import NamedTemporaryFile

from src.models.asset import Asset
from src.models.financial_goal import FinancialGoal
from src.models.financial_profile import FinancialProfile
from src.models.investment import Investment
from src.models.liability import Liability
from src.repositories.sqlite_factory import create_sqlite_repositories


def test_sqlite_persistence_roundtrip(tmp_path):
    db_file = tmp_path / "lakshmi_test.db"
    db_path = str(db_file)

    # create repositories backed by SQLite
    asset_repo, liability_repo, investment_repo, goal_repo, profile_repo = create_sqlite_repositories(db_path)

    # ensure empty
    assert asset_repo.count() == 0
    assert liability_repo.count() == 0
    assert investment_repo.count() == 0
    assert goal_repo.count() == 0
    assert profile_repo.count() == 0

    # add data
    profile = FinancialProfile(
        name="Test User",
        monthly_income=100000.0,
        monthly_expenses=40000.0,
        monthly_essential_expenses=30000.0,
        emergency_fund=150000.0,
    )
    profile_repo.add(profile)

    assets = [Asset("Cash", "Cash", 50000.0), Asset("FD", "Fixed Income", 100000.0)]
    asset_repo.add_many(assets)

    liabilities = [Liability("Home Loan", "Loan", 300000.0)]
    liability_repo.add_many(liabilities)

    investments = [Investment("Mutual Fund", "Equity", 200000.0)]
    investment_repo.add_many(investments)

    goals = [FinancialGoal("Vacation", 200000.0, 50000.0)]
    goal_repo.add_many(goals)

    # simulate application restart by creating new repository instances pointing to same DB
    asset_repo2, liability_repo2, investment_repo2, goal_repo2, profile_repo2 = create_sqlite_repositories(db_path)

    assert profile_repo2.count() == 1
    loaded_profile = profile_repo2.get_all()[0]
    assert loaded_profile.name == profile.name
    assert loaded_profile.monthly_income == profile.monthly_income

    loaded_assets = asset_repo2.get_all()
    assert len(loaded_assets) == 2
    assert any(a.name == "Cash" for a in loaded_assets)

    loaded_liabilities = liability_repo2.get_all()
    assert len(loaded_liabilities) == 1

    loaded_investments = investment_repo2.get_all()
    assert len(loaded_investments) == 1

    loaded_goals = goal_repo2.get_all()
    assert len(loaded_goals) == 1
