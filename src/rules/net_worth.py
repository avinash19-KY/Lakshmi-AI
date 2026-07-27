from collections.abc import Iterable
from typing import Protocol


class ValuedItem(Protocol):
    value: float


def total_value(items: Iterable[ValuedItem]) -> float:
    """Return the combined value of financial items."""
    return sum(item.value for item in items)


def calculate_net_worth(total_assets: float, total_liabilities: float) -> float:
    """Calculate net worth using assets minus liabilities."""
    return total_assets - total_liabilities
