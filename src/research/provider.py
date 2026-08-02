from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Protocol


@dataclass(frozen=True)
class ResearchSnapshot:
    """Normalized research facts about a single instrument.

    Fields are intentionally minimal for V1 and include clear provenance.
    """

    instrument_id: str
    name: Optional[str]
    instrument_type: Optional[str]
    price: Optional[Decimal]
    historical_annual_return: Optional[Decimal]
    as_of: Optional[str]
    source: str
    extra: dict | None = None


class ResearchProvider(Protocol):
    """Provider abstraction to fetch research snapshots for instruments.

    Providers must be read-only and deterministic.
    """

    def get_snapshot(self, instrument_id: str) -> Optional[ResearchSnapshot]:
        ...
