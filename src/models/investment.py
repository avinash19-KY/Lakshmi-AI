from dataclasses import dataclass


@dataclass(frozen=True)
class Investment:
    """A financial asset held as an investment."""

    name: str
    category: str
    value: float
