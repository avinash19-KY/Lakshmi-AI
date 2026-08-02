from src.models.cfo_context import CfoContext


class CfoQuestionService:
    """Answer a small set of explainable local CFO questions."""

    def answer(self, question: str, context: CfoContext) -> str:
        normalized = question.strip().lower()

        if "how am i doing" in normalized or "financial health" in normalized:
            return (
                f"Net worth is ₹{context.net_worth:,.0f}. "
                f"Monthly surplus is ₹{context.monthly_surplus:,.0f}. "
                f"Financial health is {context.financial_health_score:.1f}/100. "
                f"Emergency coverage is {context.emergency_fund_months:.1f} "
                f"of {context.emergency_target_months:.0f} months."
            )

        if "emergency" in normalized:
            if context.emergency_fund_gap > 0:
                return (
                    f"Emergency coverage is {context.emergency_fund_months:.1f} "
                    f"months. You need ₹{context.emergency_fund_gap:,.0f} more "
                    f"to reach the {context.emergency_target_months:.0f}-month target."
                )
            return "The emergency-fund target is fully funded."

        if "invest" in normalized or "buy" in normalized:
            return (
                f"Investment readiness is {context.investment_readiness}. "
                "Lakshmi will evaluate a specific investment only after the "
                "reserve, cash-flow, and goal checks support it."
            )

        return (
            "I can currently answer: 'How am I doing financially?', "
            "'How much more emergency fund do I need?', and "
            "'Can I invest?'"
        )
