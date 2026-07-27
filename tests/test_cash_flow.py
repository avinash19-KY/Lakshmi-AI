from src.rules.cash_flow import calculate_monthly_surplus, calculate_savings_rate


def test_monthly_surplus_subtracts_expenses_from_income() -> None:
    assert calculate_monthly_surplus(160000, 110000) == 50000


def test_savings_rate_returns_percentage_of_income() -> None:
    assert calculate_savings_rate(160000, 50000) == 31.25


def test_savings_rate_is_zero_when_income_is_not_positive() -> None:
    assert calculate_savings_rate(0, 50000) == 0.0
