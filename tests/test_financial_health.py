from src.rules.financial_health import (
    calculate_emergency_fund_score,
    calculate_financial_health_score,
    calculate_net_worth_score,
    calculate_savings_rate_score,
)


def test_emergency_score_reaches_cap_at_target_months() -> None:
    assert calculate_emergency_fund_score(12) == 40.0
    assert calculate_emergency_fund_score(18) == 40.0


def test_savings_rate_score_reaches_cap_at_target_rate() -> None:
    assert calculate_savings_rate_score(30) == 40.0
    assert calculate_savings_rate_score(40) == 40.0


def test_net_worth_score_requires_positive_net_worth() -> None:
    assert calculate_net_worth_score(1) == 20.0
    assert calculate_net_worth_score(0) == 0.0


def test_financial_health_score_combines_its_components() -> None:
    assert calculate_financial_health_score(6, 15, 100000) == 60.0
