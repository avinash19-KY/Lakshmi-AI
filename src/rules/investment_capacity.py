from src.models.investment_capacity import InvestmentCapacity


def calculate_investment_capacity(
    monthly_surplus: float,
    emergency_fund_months: float,
    *,
    emergency_target_months: float = 12,
) -> InvestmentCapacity:
    """Return a conservative ceiling for new risk capital.

    This is a guardrail, not an investment recommendation. Until the emergency
    fund reaches its target, new surplus is kept outside risky investments.
    """
    emergency_fund_ready = emergency_fund_months >= emergency_target_months

    if monthly_surplus <= 0:
        return InvestmentCapacity(
            monthly_surplus=monthly_surplus,
            maximum_new_risk_capital=0.0,
            emergency_fund_ready=emergency_fund_ready,
            reason="There is no positive monthly surplus available for new risk capital.",
        )

    if not emergency_fund_ready:
        return InvestmentCapacity(
            monthly_surplus=monthly_surplus,
            maximum_new_risk_capital=0.0,
            emergency_fund_ready=False,
            reason=(
                f"Emergency coverage is below the {emergency_target_months:.0f}-month "
                "target, so new risk capital is paused."
            ),
        )

    return InvestmentCapacity(
        monthly_surplus=monthly_surplus,
        maximum_new_risk_capital=monthly_surplus,
        emergency_fund_ready=True,
        reason=(
            "Emergency coverage is at target; the ceiling equals the positive "
            "monthly surplus before any specific investment is selected."
        ),
    )
