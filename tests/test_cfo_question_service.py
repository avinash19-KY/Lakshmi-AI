from src.models.cfo_context import CfoContext
from src.services.cfo_question_service import CfoQuestionService


def context() -> CfoContext:
    return CfoContext(
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


def test_answers_financial_health_question() -> None:
    answer = CfoQuestionService().answer("How am I doing financially?", context())

    assert "₹2,385,000" in answer
    assert "78.9/100" in answer


def test_answers_emergency_fund_question() -> None:
    answer = CfoQuestionService().answer("How much emergency fund do I need?", context())

    assert "₹570,000" in answer
    assert "12-month target" in answer


def test_answers_investment_question_with_readiness() -> None:
    answer = CfoQuestionService().answer("Can I invest?", context())

    assert "PAUSE" in answer


def test_answers_goal_question() -> None:
    answer = CfoQuestionService().answer("What is my goal?", context())

    assert "Parents' House" in answer


def test_answers_next_focus_question() -> None:
    answer = CfoQuestionService().answer("What should I focus on next?", context())

    assert "Emergency Fund" in answer
    assert "Build liquid reserves" in answer


def test_understands_natural_variations() -> None:
    service = CfoQuestionService()

    assert "Main gap" in service.answer("Where do I stand financially?", context())
    assert "₹570,000" in service.answer("How much backup should I build?", context())
    assert "PAUSE" in service.answer("Should I put money into a SIP?", context())


def test_answers_goal_progress_question() -> None:
    answer = CfoQuestionService().answer("Am I on track for my parents' house?", context())

    assert "Parents' House" in answer
    assert "₹54,167" in answer
    assert "₹4,167" in answer


def test_answers_review_request() -> None:
    answer = CfoQuestionService().answer("Give me a quick financial review", context())

    assert "Net worth: ₹2,385,000" in answer
    assert "Next focus: Emergency Fund" in answer
