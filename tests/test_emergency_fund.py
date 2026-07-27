from src.rules.emergency_fund import calculate_emergency_fund_months


def test_emergency_fund_coverage_uses_essential_expenses() -> None:
    assert calculate_emergency_fund_months(469000, 90000) == 469000 / 90000


def test_emergency_fund_coverage_is_zero_without_essential_expenses() -> None:
    assert calculate_emergency_fund_months(469000, 0) == 0.0
