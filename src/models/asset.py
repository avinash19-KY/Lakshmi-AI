from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    """An item of financial value owned by the user."""

    name: str
    category: str
    value: float
