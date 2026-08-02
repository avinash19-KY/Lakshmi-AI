from dataclasses import dataclass


@dataclass(frozen=True)
class InvestmentReadiness:
    """Explainable pre-check before evaluating a specific investment."""

    status: str
    reasons: tuple[str, ...]
