from src.rules.investment_capacity import calculate_investment_capacity


def test_capacity_is_paused_until_emergency_target_is_reached() -> None:
    capacity = calculate_investment_capacity(50000, 5.2)

    assert capacity.maximum_new_risk_capital == 0
    assert capacity.emergency_fund_ready is False
    assert "paused" in capacity.reason


def test_capacity_is_zero_when_surplus_is_not_positive() -> None:
    capacity = calculate_investment_capacity(-1000, 12)

    assert capacity.maximum_new_risk_capital == 0
    assert "no positive monthly surplus" in capacity.reason


def test_capacity_equals_surplus_when_reserve_is_ready() -> None:
    capacity = calculate_investment_capacity(50000, 12)

    assert capacity.maximum_new_risk_capital == 50000
    assert capacity.emergency_fund_ready is True
