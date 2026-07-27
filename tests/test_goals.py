from src.rules.goals import (
    calculate_goal_progress,
    calculate_monthly_goal_contribution,
    calculate_remaining_goal_amount,
)


def test_goal_progress_calculates_percentage() -> None:
    assert calculate_goal_progress(250000, 1000000) == 25.0


def test_goal_progress_is_capped_at_one_hundred_percent() -> None:
    assert calculate_goal_progress(1200000, 1000000) == 100.0


def test_remaining_goal_amount_does_not_go_below_zero() -> None:
    assert calculate_remaining_goal_amount(1200000, 1000000) == 0.0


def test_monthly_goal_contribution_splits_remaining_amount_by_duration() -> None:
    assert calculate_monthly_goal_contribution(13000000, 20) == 13000000 / 240
