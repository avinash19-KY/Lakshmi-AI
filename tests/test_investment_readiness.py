from src.rules.investment_readiness import assess_investment_readiness


def test_readiness_pauses_when_emergency_fund_is_below_target() -> None:
    result = assess_investment_readiness(
        emergency_fund_months=5.7,
        emergency_target_months=12,
        goal_funding_gap=4166.67,
        monthly_surplus=50000,
    )

    assert result.status == "PAUSE"
    assert len(result.reasons) == 2


def test_readiness_is_caution_when_goal_has_funding_gap() -> None:
    result = assess_investment_readiness(
        emergency_fund_months=12,
        emergency_target_months=12,
        goal_funding_gap=1000,
        monthly_surplus=50000,
    )

    assert result.status == "CAUTION"


def test_readiness_is_ready_when_checks_are_clear() -> None:
    result = assess_investment_readiness(
        emergency_fund_months=12,
        emergency_target_months=12,
        goal_funding_gap=0,
        monthly_surplus=50000,
    )

    assert result.status == "READY"
    assert result.reasons == ("Core reserve, cash-flow, and goal checks are clear.",)
