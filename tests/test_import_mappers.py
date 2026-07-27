from src.importer.mappers import (
    AssetMapper,
    GoalMapper,
    InvestmentMapper,
    LiabilityMapper,
)
from src.models.asset import Asset
from src.models.financial_goal import FinancialGoal
from src.models.investment import Investment
from src.models.liability import Liability


def test_asset_mapper_creates_asset() -> None:
    record = {"name": "Savings Account", "category": "Cash", "value": 250000}

    result = AssetMapper().map(record)

    assert result == Asset(name="Savings Account", category="Cash", value=250000)


def test_liability_mapper_creates_liability() -> None:
    record = {"name": "Home Loan", "category": "Debt", "value": 750000}

    result = LiabilityMapper().map(record)

    assert result == Liability(name="Home Loan", category="Debt", value=750000)


def test_goal_mapper_creates_financial_goal() -> None:
    record = {"name": "Retirement", "target_amount": 10000000, "current_amount": 2500000}

    result = GoalMapper().map(record)

    assert result == FinancialGoal(
        name="Retirement",
        target_amount=10000000,
        current_amount=2500000,
    )


def test_investment_mapper_creates_investment() -> None:
    record = {"name": "Index Fund", "category": "Equity", "value": 350000}

    result = InvestmentMapper().map(record)

    assert result == Investment(name="Index Fund", category="Equity", value=350000)


def test_mappers_map_all_records() -> None:
    records = [
        {"name": "Savings", "category": "Cash", "value": 100000},
        {"name": "Stocks", "category": "Equity", "value": 200000},
    ]

    result = AssetMapper().map_all(records)

    assert result == [
        Asset(name="Savings", category="Cash", value=100000),
        Asset(name="Stocks", category="Equity", value=200000),
    ]
