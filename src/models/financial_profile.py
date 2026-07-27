from dataclasses import dataclass


@dataclass
class FinancialProfile:
    """
    Represents the user's financial profile.
    """

    name: str
    monthly_income: float
    monthly_expenses: float
    monthly_essential_expenses: float
    emergency_fund: float
