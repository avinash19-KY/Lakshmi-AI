def calculate_goal_progress(current_amount: float, target_amount: float) -> float:
    """Return goal progress as a percentage, capped at 100%."""
    if target_amount <= 0:
        return 0.0

    return min((current_amount / target_amount) * 100, 100.0)


def calculate_remaining_goal_amount(current_amount: float, target_amount: float) -> float:
    """Return the amount still needed to reach a goal."""
    return max(target_amount - current_amount, 0.0)


def calculate_monthly_goal_contribution(
    remaining_amount: float, duration_years: int
) -> float:
    """Return the monthly contribution required without assuming investment returns."""
    if duration_years <= 0:
        return 0.0

    return remaining_amount / (duration_years * 12)


def calculate_goal_funding_gap(
    remaining_amount: float,
    duration_years: int,
    monthly_surplus: float,
) -> float:
    """Compare required monthly goal funding with current monthly surplus."""
    required_contribution = calculate_monthly_goal_contribution(
        remaining_amount, duration_years
    )
    return required_contribution - monthly_surplus
