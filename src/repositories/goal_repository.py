from __future__ import annotations

from src.models.financial_goal import FinancialGoal
from src.repositories.in_memory import InMemoryRepository


class GoalRepository(InMemoryRepository[FinancialGoal]):
    """Repository for FinancialGoal domain objects."""
    pass
