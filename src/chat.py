from src.models.cfo_context import CfoContext
from src.rules.cash_flow import calculate_monthly_surplus, calculate_savings_rate
from src.rules.emergency_fund import (
    calculate_emergency_fund_gap,
    calculate_emergency_fund_months,
)
from src.rules.financial_health import calculate_financial_health_score
from src.rules.net_worth import calculate_net_worth, total_value
from src.rules.investment_readiness import assess_investment_readiness
from src.services.cfo_question_service import CfoQuestionService
from src.services.profile_service import ProfileService


def build_context(service: ProfileService) -> CfoContext:
    profile = service.profile_repository.get_all()[0]
    assets = service.asset_repository.get_all()
    liabilities = service.liability_repository.get_all()
    goals = service.goal_repository.get_all()

    monthly_surplus = calculate_monthly_surplus(
        profile.monthly_income, profile.monthly_expenses
    )
    emergency_months = calculate_emergency_fund_months(
        profile.emergency_fund, profile.monthly_essential_expenses
    )
    net_worth = calculate_net_worth(total_value(assets), total_value(liabilities))
    savings_rate = calculate_savings_rate(profile.monthly_income, monthly_surplus)
    health_score = calculate_financial_health_score(
        emergency_months, savings_rate, net_worth
    )

    goal_gap = 0.0
    if goals:
        goal = goals[0]
        remaining = max(goal.target_amount - goal.current_amount, 0.0)
        goal_gap = remaining / (20 * 12) - monthly_surplus

    readiness = assess_investment_readiness(
        emergency_fund_months=emergency_months,
        emergency_target_months=12,
        goal_funding_gap=goal_gap,
        monthly_surplus=monthly_surplus,
    )

    return CfoContext(
        net_worth=net_worth,
        monthly_surplus=monthly_surplus,
        emergency_fund_months=emergency_months,
        emergency_target_months=12,
        emergency_fund_gap=calculate_emergency_fund_gap(
            profile.emergency_fund, profile.monthly_essential_expenses
        ),
        financial_health_score=health_score,
        investment_readiness=readiness.status,
    )


def main() -> None:
    service = ProfileService()
    service.load_data()
    context = build_context(service)
    question_service = CfoQuestionService()

    print("Lakshmi AI local CFO chat. Type 'exit' to stop.")
    while True:
        question = input("You: ")
        if question.strip().lower() in {"exit", "quit"}:
            break
        print(f"Lakshmi: {question_service.answer(question, context)}")


if __name__ == "__main__":
    main()
