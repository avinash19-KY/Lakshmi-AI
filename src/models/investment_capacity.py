from dataclasses import dataclass


@dataclass(frozen=True)
class InvestmentCapacity:
    """A conservative ceiling for new risk-taking from monthly cash flow."""

    monthly_surplus: float
    maximum_new_risk_capital: float
    emergency_fund_ready: bool
    reason: str
