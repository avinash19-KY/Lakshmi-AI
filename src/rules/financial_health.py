def calculate_emergency_fund_score(
    emergency_fund_months: float, target_months: float = 12
) -> float:
    """Score emergency resilience on a 40-point scale."""
    if target_months <= 0:
        return 0.0

    return min((emergency_fund_months / target_months) * 40, 40.0)


def calculate_savings_rate_score(
    savings_rate: float, target_savings_rate: float = 30
) -> float:
    """Score monthly saving capacity on a 40-point scale."""
    if target_savings_rate <= 0:
        return 0.0

    return min((savings_rate / target_savings_rate) * 40, 40.0)


def calculate_net_worth_score(net_worth: float) -> float:
    """Award 20 points when assets exceed liabilities."""
    return 20.0 if net_worth > 0 else 0.0


def calculate_financial_health_score(
    emergency_fund_months: float, savings_rate: float, net_worth: float
) -> float:
    """Return an explainable 100-point financial health score."""
    return (
        calculate_emergency_fund_score(emergency_fund_months)
        + calculate_savings_rate_score(savings_rate)
        + calculate_net_worth_score(net_worth)
    )
