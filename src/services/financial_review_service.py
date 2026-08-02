from src.models.cfo_context import CfoContext


class FinancialReviewService:
    """Create a short, decision-focused review from the CFO context."""

    def build_review(self, context: CfoContext) -> str:
        return "\n".join(
            [
                f"Net worth: ₹{context.net_worth:,.0f}",
                f"Monthly surplus: ₹{context.monthly_surplus:,.0f}",
                f"Financial health: {context.financial_health_score:.1f}/100",
                (
                    f"Emergency fund: {context.emergency_fund_months:.1f}/"
                    f"{context.emergency_target_months:.0f} months "
                    f"(₹{context.emergency_fund_gap:,.0f} to go)"
                ),
                f"Goal: {context.primary_goal_name}",
                f"Investment readiness: {context.investment_readiness}",
                f"Next focus: {context.focus_area} — {context.focus_reason}",
            ]
        )
