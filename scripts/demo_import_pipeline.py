from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime
import sys

ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIRECTORY))

from src.services.profile_service import ProfileService
from src.rules.asset_allocation import (
    calculate_allocation_by_category,
    calculate_allocation_percentages,
)
from src.rules.cash_flow import calculate_monthly_surplus, calculate_savings_rate
from src.rules.emergency_fund import calculate_emergency_fund_months
from src.rules.financial_health import (
    calculate_emergency_fund_score,
    calculate_financial_health_score,
    calculate_net_worth_score,
    calculate_savings_rate_score,
)
from src.rules.goals import (
    calculate_goal_progress,
    calculate_monthly_goal_contribution,
    calculate_remaining_goal_amount,
)
from src.rules.net_worth import calculate_net_worth, total_value


def banner() -> None:
    ist_time = datetime.now(ZoneInfo("Asia/Kolkata"))
    print("=" * 50)
    print("💰 Lakshmi AI Import Demo")
    print("Import source: data/import_examples")
    print("=" * 50)
    print(f"Date: {ist_time.strftime('%d-%b-%Y %I:%M:%S %p IST')}")
    print()


def main() -> None:
    banner()
    sample_directory = Path(__file__).resolve().parents[1] / "data" / "import_examples"
    service = ProfileService(sample_directory)
    service.load_data()

    profile = service.profile_repository.get_all()[0]
    assets = service.asset_repository.get_all()
    liabilities = service.liability_repository.get_all()
    goals = service.goal_repository.get_all()

    total_assets = total_value(assets)
    total_liabilities = total_value(liabilities)
    net_worth = calculate_net_worth(total_assets, total_liabilities)
    allocation_by_category = calculate_allocation_by_category(assets)
    allocation_percentages = calculate_allocation_percentages(allocation_by_category)
    monthly_surplus = calculate_monthly_surplus(
        profile.monthly_income, profile.monthly_expenses
    )
    savings_rate = calculate_savings_rate(profile.monthly_income, monthly_surplus)
    emergency_fund_months = calculate_emergency_fund_months(
        profile.emergency_fund, profile.monthly_essential_expenses
    )
    emergency_fund_score = calculate_emergency_fund_score(emergency_fund_months)
    savings_rate_score = calculate_savings_rate_score(savings_rate)
    net_worth_score = calculate_net_worth_score(net_worth)
    financial_health_score = calculate_financial_health_score(
        emergency_fund_months, savings_rate, net_worth
    )

    print("Financial Profile")
    print("-" * 60)
    print(f"Name              : {profile.name}")
    print(f"Monthly Income    : ₹{profile.monthly_income:,.2f}")
    print(f"Monthly Expenses  : ₹{profile.monthly_expenses:,.2f}")
    print(f"Essential Expenses: ₹{profile.monthly_essential_expenses:,.2f}")
    print(f"Emergency Fund    : ₹{profile.emergency_fund:,.2f}")

    print()
    print("Financial Snapshot")
    print("-" * 60)
    print(f"Total Assets      : ₹{total_assets:,.2f}")
    print(f"Total Liabilities : ₹{total_liabilities:,.2f}")
    print(f"Net Worth         : ₹{net_worth:,.2f}")

    print()
    print("Cash Flow & Resilience")
    print("-" * 60)
    print(f"Monthly Surplus   : ₹{monthly_surplus:,.2f}")
    print(f"Savings Rate      : {savings_rate:.1f}%")
    print(f"Emergency Coverage: {emergency_fund_months:.1f} months")

    for goal in goals:
        progress = calculate_goal_progress(goal.current_amount, goal.target_amount)
        remaining_amount = calculate_remaining_goal_amount(
            goal.current_amount, goal.target_amount
        )
        monthly_for_15_years = calculate_monthly_goal_contribution(
            remaining_amount, 15
        )
        monthly_for_20_years = calculate_monthly_goal_contribution(
            remaining_amount, 20
        )

        print()
        print(f"Goal: {goal.name}")
        print("-" * 60)
        print(f"Target Amount     : ₹{goal.target_amount:,.2f}")
        print(f"Current Allocation: ₹{goal.current_amount:,.2f}")
        print(f"Progress          : {progress:.1f}%")
        print(f"Remaining         : ₹{remaining_amount:,.2f}")
        print("Full-value funding scenarios (before investment returns):")
        print(f"15 years          : ₹{monthly_for_15_years:,.2f}/month")
        print(f"20 years          : ₹{monthly_for_20_years:,.2f}/month")

    print()
    print("Asset Allocation")
    print("-" * 60)
    for category in sorted(allocation_by_category):
        amount = allocation_by_category[category]
        percentage = allocation_percentages[category]
        print(f"{category:<18}: ₹{amount:>12,.2f} ({percentage:>5.1f}%)")

    print()
    print("Financial Health Score")
    print("-" * 60)
    print(f"Overall Score      : {financial_health_score:.1f} / 100")
    print(f"Emergency Reserve  : {emergency_fund_score:.1f} / 40 (12-month target)")
    print(f"Savings Capacity   : {savings_rate_score:.1f} / 40 (30% target)")
    print(f"Net Worth Position : {net_worth_score:.1f} / 20 (positive target)")


if __name__ == "__main__":
    main()
