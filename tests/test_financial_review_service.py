from src.models.cfo_context import CfoContext
from src.services.financial_review_service import FinancialReviewService


def test_review_is_concise_and_decision_focused() -> None:
    context = CfoContext(
        net_worth=2385000,
        monthly_surplus=50000,
        emergency_fund_months=5.7,
        emergency_target_months=12,
        emergency_fund_gap=570000,
        financial_health_score=78.9,
        investment_readiness="PAUSE",
        focus_area="Emergency Fund",
        focus_reason="Build liquid reserves first.",
        primary_goal_name="Parents' House",
        primary_goal_remaining=13000000,
        primary_goal_monthly_required=54166.67,
        primary_goal_funding_gap=4166.67,
    )

    review = FinancialReviewService().build_review(context)

    assert "Net worth: ₹2,385,000" in review
    assert "Investment readiness: PAUSE" in review
    assert "Next focus: Emergency Fund" in review
