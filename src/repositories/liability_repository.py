from __future__ import annotations

from src.models.liability import Liability
from src.repositories.in_memory import InMemoryRepository


class LiabilityRepository(InMemoryRepository[Liability]):
    """Repository for Liability domain objects."""
    pass
