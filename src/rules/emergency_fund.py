def calculate_emergency_fund_months(
    emergency_fund: float, monthly_essential_expenses: float
) -> float:
    """Return how many months of essential expenses the fund can cover."""
    if monthly_essential_expenses <= 0:
        return 0.0

    return emergency_fund / monthly_essential_expenses


def calculate_emergency_fund_target(
    monthly_essential_expenses: float, target_months: float = 12
) -> float:
    """Return the cash amount required to cover the target months."""
    if monthly_essential_expenses <= 0 or target_months <= 0:
        return 0.0

    return monthly_essential_expenses * target_months


def calculate_emergency_fund_gap(
    emergency_fund: float,
    monthly_essential_expenses: float,
    target_months: float = 12,
) -> float:
    """Return how much more is needed to reach the emergency-fund target."""
    target_amount = calculate_emergency_fund_target(
        monthly_essential_expenses, target_months
    )
    return max(target_amount - emergency_fund, 0.0)
