from src.models.asset import Asset
from src.models.liability import Liability
from src.rules.net_worth import calculate_net_worth, total_value


def test_total_value_adds_asset_values() -> None:
    assets = [
        Asset("Savings", "Cash", 100000),
        Asset("Mutual fund", "Equity", 250000),
    ]

    assert total_value(assets) == 350000


def test_total_value_returns_zero_for_no_items() -> None:
    assert total_value([]) == 0


def test_calculate_net_worth_subtracts_liabilities() -> None:
    liabilities = [Liability("Loan", "Personal loan", 25000)]

    assert calculate_net_worth(350000, total_value(liabilities)) == 325000
