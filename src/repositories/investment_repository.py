from __future__ import annotations

from src.models.investment import Investment
from src.repositories.in_memory import InMemoryRepository


class InvestmentRepository(InMemoryRepository[Investment]):
    """Repository for Investment domain objects."""
    pass
