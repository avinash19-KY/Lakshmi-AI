from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Defines the operations supported by a repository."""

    @abstractmethod
    def add(self, item: T) -> str:
        raise NotImplementedError

    @abstractmethod
    def add_many(self, items: Iterable[T]) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, item_id: str) -> T | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, item_id: str, item: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        raise NotImplementedError
