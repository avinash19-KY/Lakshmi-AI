from dataclasses import dataclass


@dataclass(frozen=True)
class CfoContext:
    """Facts the local CFO question layer is allowed to use."""

    net_worth: float
    monthly_surplus: float
    emergency_fund_months: float
    emergency_target_months: float
    emergency_fund_gap: float
    financial_health_score: float
    investment_readiness: str
    focus_area: str
    focus_reason: str
    primary_goal_name: str
    primary_goal_remaining: float
    primary_goal_monthly_required: float
    primary_goal_funding_gap: float
