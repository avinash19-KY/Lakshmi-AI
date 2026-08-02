from __future__ import annotations

from src.models.portfolio_insight import PortfolioInsight


def build_portfolio_focus_insights(
    emergency_fund_months: float,
    savings_rate: float,
    net_worth: float,
    allocation_by_category: dict[str, float],
    *,
    emergency_target_months: float = 12,
    savings_target_rate: float = 30,
    concentration_threshold: float = 50,
) -> list[PortfolioInsight]:
    """Return the weakest areas to focus on first."""
    insights: list[PortfolioInsight] = []

    _add_emergency_fund_insight(
        insights,
        emergency_fund_months,
        emergency_target_months,
    )
    _add_savings_insight(
        insights,
        savings_rate,
        savings_target_rate,
    )
    _add_net_worth_insight(insights, net_worth)
    _add_concentration_insight(
        insights,
        allocation_by_category,
        concentration_threshold,
    )

    return sorted(insights, key=lambda insight: (insight.priority, insight.area))


def _add_emergency_fund_insight(
    insights: list[PortfolioInsight],
    emergency_fund_months: float,
    emergency_target_months: float,
) -> None:
    if emergency_fund_months >= emergency_target_months:
        return

    priority = 1 if emergency_fund_months < 6 else 2
    reason = (
        f"Emergency coverage is {emergency_fund_months:.1f} months, below the "
        f"{emergency_target_months:.0f}-month target."
    )
    recommendation = (
        "Build liquid reserves first. Keep new risky investments small until "
        "the emergency fund target is reached."
    )
    insights.append(
        PortfolioInsight(
            area="Emergency Fund",
            priority=priority,
            reason=reason,
            recommendation=recommendation,
        )
    )


def _add_savings_insight(
    insights: list[PortfolioInsight],
    savings_rate: float,
    savings_target_rate: float,
) -> None:
    if savings_rate >= savings_target_rate:
        return

    priority = 2 if savings_rate < 20 else 3
    reason = (
        f"Savings rate is {savings_rate:.1f}%, below the {savings_target_rate:.0f}% "
        "target."
    )
    recommendation = (
        "Increase monthly surplus before expanding risk. A higher savings rate "
        "creates more room for goals and future investments."
    )
    insights.append(
        PortfolioInsight(
            area="Savings Rate",
            priority=priority,
            reason=reason,
            recommendation=recommendation,
        )
    )


def _add_net_worth_insight(
    insights: list[PortfolioInsight],
    net_worth: float,
) -> None:
    if net_worth > 0:
        return

    insights.append(
        PortfolioInsight(
            area="Net Worth",
            priority=1,
            reason="Net worth is zero or negative, so liabilities are still pressuring the balance sheet.",
            recommendation=(
                "Focus on debt reduction, cash discipline, and emergency reserves "
                "before adding speculative positions."
            ),
        )
    )


def _add_concentration_insight(
    insights: list[PortfolioInsight],
    allocation_by_category: dict[str, float],
    concentration_threshold: float,
) -> None:
    total_assets = sum(allocation_by_category.values())
    if total_assets <= 0 or not allocation_by_category:
        return

    top_category, top_value = max(
        allocation_by_category.items(), key=lambda item: item[1]
    )
    top_share = (top_value / total_assets) * 100

    if top_share <= concentration_threshold:
        return

    insights.append(
        PortfolioInsight(
            area="Concentration Risk",
            priority=3,
            reason=(
                f"{top_category} makes up {top_share:.1f}% of total assets, "
                f"which is above the {concentration_threshold:.0f}% alert level."
            ),
            recommendation=(
                "Prefer the next new investment to go into the weaker or less "
                "represented part of the portfolio."
            ),
        )
    )
