from src.rules.asset_allocation import calculate_allocation_by_category
from src.rules.portfolio_intelligence import build_portfolio_focus_insights
from src.models.asset import Asset


def test_portfolio_intelligence_prioritizes_emergency_fund_when_low() -> None:
    insights = build_portfolio_focus_insights(
        emergency_fund_months=5.2,
        savings_rate=31.2,
        net_worth=2344000,
        allocation_by_category={
            "Cash": 519000,
            "Equity": 667000,
            "Retirement": 1158000,
        },
    )

    assert insights[0].area == "Emergency Fund"
    assert "below the 12-month target" in insights[0].reason


def test_portfolio_intelligence_flags_low_savings_rate() -> None:
    insights = build_portfolio_focus_insights(
        emergency_fund_months=12,
        savings_rate=18,
        net_worth=100000,
        allocation_by_category={"Cash": 100000},
    )

    assert any(insight.area == "Savings Rate" for insight in insights)


def test_portfolio_intelligence_returns_no_insights_when_healthy() -> None:
    insights = build_portfolio_focus_insights(
        emergency_fund_months=12,
        savings_rate=35,
        net_worth=100000,
        allocation_by_category={"Cash": 50000, "Equity": 50000},
    )

    assert insights == []


def test_portfolio_intelligence_flags_concentration_risk() -> None:
    assets = [
        Asset("Savings", "Cash", 100000),
        Asset("Mutual fund", "Equity", 100000),
        Asset("EPF", "Retirement", 400000),
    ]
    allocation_by_category = calculate_allocation_by_category(assets)

    insights = build_portfolio_focus_insights(
        emergency_fund_months=12,
        savings_rate=35,
        net_worth=600000,
        allocation_by_category=allocation_by_category,
        concentration_threshold=50,
    )

    assert any(insight.area == "Concentration Risk" for insight in insights)
