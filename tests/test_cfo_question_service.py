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


def test_explains_supported_questions() -> None:
    answer = CfoQuestionService().answer("What is my goal?", context())

    assert "How am I doing financially?" in answer
