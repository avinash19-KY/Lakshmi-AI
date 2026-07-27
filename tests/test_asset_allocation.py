from src.models.asset import Asset
from src.rules.asset_allocation import (
    calculate_allocation_by_category,
    calculate_allocation_percentages,
)


def test_allocation_groups_assets_by_category() -> None:
    assets = [
        Asset("Savings", "Cash", 100000),
        Asset("Emergency fund", "Cash", 200000),
        Asset("Fund", "Equity", 300000),
    ]

    assert calculate_allocation_by_category(assets) == {
        "Cash": 300000,
        "Equity": 300000,
    }


def test_allocation_percentages_are_calculated_from_total_assets() -> None:
    percentages = calculate_allocation_percentages(
        {"Cash": 300000, "Equity": 300000}
    )

    assert percentages == {"Cash": 50.0, "Equity": 50.0}


def test_allocation_percentages_handle_zero_value_assets() -> None:
    assert calculate_allocation_percentages({"Cash": 0}) == {"Cash": 0.0}
