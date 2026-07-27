from collections import defaultdict
from collections.abc import Iterable

from src.models.asset import Asset


def calculate_allocation_by_category(assets: Iterable[Asset]) -> dict[str, float]:
    """Group asset values by their category."""
    allocation: defaultdict[str, float] = defaultdict(float)

    for asset in assets:
        allocation[asset.category] += asset.value

    return dict(allocation)


def calculate_allocation_percentages(
    allocation_by_category: dict[str, float]
) -> dict[str, float]:
    """Convert category values into portfolio percentages."""
    total_assets = sum(allocation_by_category.values())
    if total_assets <= 0:
        return {category: 0.0 for category in allocation_by_category}

    return {
        category: (value / total_assets) * 100
        for category, value in allocation_by_category.items()
    }
