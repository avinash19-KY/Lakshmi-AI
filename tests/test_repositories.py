import pytest

from src.models.asset import Asset
from src.models.financial_goal import FinancialGoal
from src.models.financial_profile import FinancialProfile
from src.models.investment import Investment
from src.models.liability import Liability
from src.repositories.asset_repository import AssetRepository
from src.repositories.financial_profile_repository import FinancialProfileRepository
from src.repositories.goal_repository import GoalRepository
from src.repositories.investment_repository import InvestmentRepository
from src.repositories.liability_repository import LiabilityRepository


def test_asset_repository_crud_operations() -> None:
    repository = AssetRepository()
    asset = Asset(name="Savings", category="Cash", value=100000)

    item_id = repository.add(asset)
    assert repository.count() == 1
    assert repository.get_by_id(item_id) == asset
    assert repository.get_all() == [asset]

    updated_asset = Asset(name="Savings", category="Cash", value=110000)
    repository.update(item_id, updated_asset)
    assert repository.get_by_id(item_id) == updated_asset

    repository.delete(item_id)
    assert repository.count() == 0
    repository.clear()
    assert repository.count() == 0


def test_goal_repository_add_many_and_clear() -> None:
    repository = GoalRepository()
    goals = [
        FinancialGoal(name="House", target_amount=5000000, current_amount=250000),
        FinancialGoal(name="Car", target_amount=1500000, current_amount=300000),
    ]

    ids = repository.add_many(goals)
    assert len(ids) == 2
    assert repository.count() == 2
    assert repository.get_all() == goals

    repository.clear()
    assert repository.count() == 0


def test_investment_repository_crud_operations() -> None:
    repository = InvestmentRepository()
    investment = Investment(name="Index Fund", category="Equity", value=350000)

    item_id = repository.add(investment)
    assert repository.count() == 1
    assert repository.get_by_id(item_id) == investment
    assert repository.get_all() == [investment]

    repository.delete(item_id)
    assert repository.count() == 0


def test_financial_profile_repository_single_profile() -> None:
    repository = FinancialProfileRepository()
    profile = FinancialProfile(
        name="Test User",
        monthly_income=120000,
        monthly_expenses=80000,
        monthly_essential_expenses=60000,
        emergency_fund=300000,
    )

    profile_id = repository.add(profile)
    assert repository.get_by_id(profile_id) == profile
    assert repository.count() == 1

    same_profile = repository.get_all()[0]
    assert same_profile == profile


def test_liability_repository_update_nonexistent_raises_key_error() -> None:
    repository = LiabilityRepository()
    liability = Liability(name="Loan", category="Debt", value=500000)

    with pytest.raises(KeyError):
        repository.update("invalid-id", liability)
