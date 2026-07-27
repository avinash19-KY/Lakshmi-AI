def calculate_monthly_surplus(monthly_income: float, monthly_expenses: float) -> float:
    """Return the money remaining after recorded monthly expenses."""
    return monthly_income - monthly_expenses


def calculate_savings_rate(monthly_income: float, monthly_surplus: float) -> float:
    """Return the monthly surplus as a percentage of income."""
    if monthly_income <= 0:
        return 0.0

    return (monthly_surplus / monthly_income) * 100
