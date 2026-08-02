from src.rules.emergency_fund import (
    calculate_emergency_fund_gap,
    calculate_emergency_fund_months,
    calculate_emergency_fund_target,
)


def test_emergency_fund_coverage_uses_essential_expenses() -> None:
    assert calculate_emergency_fund_months(469000, 90000) == 469000 / 90000


def test_emergency_fund_coverage_is_zero_without_essential_expenses() -> None:
    assert calculate_emergency_fund_months(469000, 0) == 0.0


def test_emergency_fund_target_and_gap() -> None:
    assert calculate_emergency_fund_target(90000, 12) == 1080000
    assert calculate_emergency_fund_gap(469000, 90000, 12) == 611000


def test_emergency_fund_gap_does_not_go_below_zero() -> None:
    assert calculate_emergency_fund_gap(1200000, 90000, 12) == 0.0
