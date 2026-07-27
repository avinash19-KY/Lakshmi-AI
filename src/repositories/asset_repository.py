from __future__ import annotations

from src.models.asset import Asset
from src.repositories.in_memory import InMemoryRepository


class AssetRepository(InMemoryRepository[Asset]):
    """Repository for Asset domain objects."""
    pass
