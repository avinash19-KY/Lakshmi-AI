from __future__ import annotations

from src.models.financial_profile import FinancialProfile
from src.repositories.in_memory import InMemoryRepository


class FinancialProfileRepository(InMemoryRepository[FinancialProfile]):
    """Repository for FinancialProfile domain objects."""
    pass
