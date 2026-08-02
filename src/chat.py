from src.models.cfo_context import CfoContext
from src.rules.cash_flow import calculate_monthly_surplus, calculate_savings_rate
from src.rules.emergency_fund import (
    calculate_emergency_fund_gap,
    calculate_emergency_fund_months,
)
from src.rules.financial_health import calculate_financial_health_score
from src.rules.investment_readiness import assess_investment_readiness
from src.rules.net_worth import calculate_net_worth, total_value
from src.rules.portfolio_intelligence import build_portfolio_focus_insights
from src.services.cfo_question_service import CfoQuestionService
from src.services.decision_journal_service import DecisionJournalService
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
    goal_name = "No goal recorded"
    goal_remaining = 0.0
    goal_monthly_required = 0.0
    if goals:
        goal = goals[0]
        goal_name = goal.name
        goal_remaining = max(goal.target_amount - goal.current_amount, 0.0)
        goal_monthly_required = goal_remaining / (20 * 12)
        goal_gap = goal_monthly_required - monthly_surplus

    readiness = assess_investment_readiness(
        emergency_fund_months=emergency_months,
        emergency_target_months=12,
        goal_funding_gap=goal_gap,
        monthly_surplus=monthly_surplus,
    )

    allocation_by_category: dict[str, float] = {}
    for asset in assets:
        allocation_by_category[asset.category] = (
            allocation_by_category.get(asset.category, 0.0) + asset.value
        )
    focus_insights = build_portfolio_focus_insights(
        emergency_fund_months=emergency_months,
        savings_rate=savings_rate,
        net_worth=net_worth,
        allocation_by_category=allocation_by_category,
    )
    focus_area = focus_insights[0].area if focus_insights else "No major focus area"
    focus_reason = (
        focus_insights[0].recommendation
        if focus_insights
        else "The current financial picture is within the configured guardrails."
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
        focus_area=focus_area,
        focus_reason=focus_reason,
        primary_goal_name=goal_name,
        primary_goal_remaining=goal_remaining,
        primary_goal_monthly_required=goal_monthly_required,
        primary_goal_funding_gap=goal_gap,
    )


def main() -> None:
    service = ProfileService()
    service.load_data()
    context = build_context(service)
    question_service = CfoQuestionService()
    journal = DecisionJournalService(
        service.data_directory / "decision_journal.json"
    )

    print("Lakshmi AI local CFO chat. Type 'exit' to stop.")
    while True:
        question = input("You: ")
        normalized = question.strip().lower()
        if normalized in {"exit", "quit"}:
            break
        if normalized.startswith("remember "):
            entry = journal.add(question.strip()[9:])
            print(f"Lakshmi: I’ll remember that from {entry.created_at[:10]}.")
            continue
        if "show" in normalized and (
            "decision" in normalized or "journal" in normalized or "memory" in normalized
        ):
            entries = journal.recent()
            if not entries:
                print("Lakshmi: Your decision journal is empty.")
            else:
                for entry in entries:
                    print(f"Lakshmi: {entry.created_at[:10]} — {entry.note}")
            continue
        print(f"Lakshmi: {question_service.answer(question, context)}")


if __name__ == "__main__":
    main()
