def calculate_emergency_fund_months(
    emergency_fund: float, monthly_essential_expenses: float
) -> float:
    """Return how many months of essential expenses the fund can cover."""
    if monthly_essential_expenses <= 0:
        return 0.0

    return emergency_fund / monthly_essential_expenses
