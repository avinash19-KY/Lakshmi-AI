from __future__ import annotations

from uuid import uuid4
from typing import Generic, TypeVar

from src.repositories.base import Repository

T = TypeVar("T")


class InMemoryRepository(Repository[T], Generic[T]):
    """Stores domain objects in memory."""

    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def add(self, item: T) -> str:
        item_id = str(uuid4())
        self._items[item_id] = item
        return item_id

    def add_many(self, items: list[T]) -> list[str]:
        return [self.add(item) for item in items]

    def get_all(self) -> list[T]:
        return list(self._items.values())

    def get_by_id(self, item_id: str) -> T | None:
        return self._items.get(item_id)

    def update(self, item_id: str, item: T) -> None:
        if item_id not in self._items:
            raise KeyError(f"Item with id '{item_id}' does not exist.")
        self._items[item_id] = item

    def delete(self, item_id: str) -> None:
        if item_id not in self._items:
            raise KeyError(f"Item with id '{item_id}' does not exist.")
        del self._items[item_id]

    def clear(self) -> None:
        self._items.clear()

    def count(self) -> int:
        return len(self._items)
