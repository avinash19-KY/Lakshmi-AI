from dataclasses import dataclass


@dataclass(frozen=True)
class FinancialGoal:
    """A personal financial outcome that Lakshmi AI tracks."""

    name: str
    target_amount: float
    current_amount: float
