from src.models.investment_readiness import InvestmentReadiness


def assess_investment_readiness(
    *,
    emergency_fund_months: float,
    emergency_target_months: float,
    goal_funding_gap: float,
    monthly_surplus: float,
) -> InvestmentReadiness:
    """Assess whether a new investment should be evaluated at all.

    This gate does not recommend an asset, amount, or expected return. It only
    checks whether the surrounding financial conditions support further review.
    """
    reasons: list[str] = []

    if emergency_fund_months < emergency_target_months:
        reasons.append(
            f"Emergency coverage is below the {emergency_target_months:.0f}-month target."
        )

    if monthly_surplus <= 0:
        reasons.append("Monthly surplus is not positive.")

    if goal_funding_gap > 0:
        reasons.append(
            f"The current goal plan has a ₹{goal_funding_gap:,.2f}/month funding gap."
        )

    if emergency_fund_months < emergency_target_months:
        status = "PAUSE"
    elif reasons:
        status = "CAUTION"
    else:
        status = "READY"

    if not reasons:
        reasons.append("Core reserve, cash-flow, and goal checks are clear.")

    return InvestmentReadiness(status=status, reasons=tuple(reasons))
