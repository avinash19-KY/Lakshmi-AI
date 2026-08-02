from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioInsight:
    """A simple, explainable portfolio intelligence recommendation."""

    area: str
    priority: int
    reason: str
    recommendation: str
