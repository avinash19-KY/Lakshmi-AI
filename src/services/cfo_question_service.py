from src.models.cfo_context import CfoContext
from src.services.financial_review_service import FinancialReviewService


class CfoQuestionService:
    """Answer a small set of explainable local CFO questions."""

    def __init__(self) -> None:
        self.review_service = FinancialReviewService()

    def answer(self, question: str, context: CfoContext) -> str:
        normalized = " ".join(question.strip().lower().split())

        if _matches(
            normalized,
            "review",
            "report",
            "briefing",
            "morning update",
            "give me an update",
        ):
            return self.review_service.build_review(context)

        if _matches(
            normalized,
            "how am i doing",
            "where do i stand",
            "financial health",
            "financial position",
            "overall status",
            "financial summary",
        ):
            return (
                f"You’re financially positive: net worth ₹{context.net_worth:,.0f}, "
                f"monthly surplus ₹{context.monthly_surplus:,.0f}, and health "
                f"{context.financial_health_score:.1f}/100. "
                f"Main gap: emergency coverage is {context.emergency_fund_months:.1f} "
                f"of {context.emergency_target_months:.0f} months."
            )

        if _matches(
            normalized,
            "goal",
            "parents' house",
            "parents house",
            "on track",
        ):
            if context.primary_goal_name == "No goal recorded":
                return "No financial goal has been recorded yet."
            if context.primary_goal_funding_gap > 0:
                return (
                    f"{context.primary_goal_name} needs ₹{context.primary_goal_monthly_required:,.0f} "
                    f"per month over 20 years. Your current surplus leaves a "
                    f"₹{context.primary_goal_funding_gap:,.0f}/month gap."
                )
            return (
                f"{context.primary_goal_name} needs about "
                f"₹{context.primary_goal_monthly_required:,.0f}/month over 20 years. "
                "Your current surplus covers that baseline."
            )

        if _matches(
            normalized,
            "emergency",
            "backup",
            "rainy day",
            "safety net",
            "job loss",
            "reserve",
        ):
            if context.emergency_fund_gap > 0:
                return (
                    f"You’re covered for {context.emergency_fund_months:.1f} months. "
                    f"Add ₹{context.emergency_fund_gap:,.0f} to reach the "
                    f"{context.emergency_target_months:.0f}-month target."
                )
            return "The emergency-fund target is fully funded."

        if _matches(
            normalized,
            "invest",
            "buy",
            "put money",
            "deploy",
            "stock",
            "sip",
            "mutual fund",
        ):
            return (
                f"Investment readiness: {context.investment_readiness}. "
                "I’ll consider a specific investment only after the reserve, "
                "cash-flow, and goal checks support it."
            )

        if _matches(
            normalized,
            "focus",
            "next step",
            "priority",
            "what should i do",
            "where should i improve",
            "what needs attention",
        ):
            return f"Focus on {context.focus_area}. {context.focus_reason}"

        if _matches(normalized, "net worth", "how much do i have"):
            return f"Your current net worth is ₹{context.net_worth:,.0f}."

        return (
            "I can currently answer: 'How am I doing financially?', "
            "'How much more emergency fund do I need?', and "
            "'Can I invest?'"
        )


def _matches(question: str, *phrases: str) -> bool:
    return any(phrase in question for phrase in phrases)
