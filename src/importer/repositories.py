from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Repository(ABC):
    """Stores normalized import records."""

    @abstractmethod
    def save(self, records: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def retrieve(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class InMemoryRepository(Repository):
    """Keeps import records in memory."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def save(self, records: list[dict[str, Any]]) -> None:
        self._records = [dict(record) for record in records]

    def retrieve(self) -> list[dict[str, Any]]:
        return [dict(record) for record in self._records]
