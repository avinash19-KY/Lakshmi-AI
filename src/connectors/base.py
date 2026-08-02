from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class ConnectorHolding:
    """Canonical holding representation produced by connectors.

    Keep this minimal to allow mapping into existing domain models.
    """

    external_id: str
    name: str
    category: str
    value: float
    domain: str  # 'investment' or 'asset'
    as_of: Optional[datetime] = None


class PortfolioConnector(ABC):
    """Connector interface for read-only portfolio sources."""

    @abstractmethod
    def name(self) -> str:
        """Human-friendly connector name."""

    @abstractmethod
    def fetch_holdings(self) -> List[ConnectorHolding]:
        """Fetch holdings from the provider and return a list of canonical holdings.

        Implementations must NOT modify external portfolios. Read-only only.
        """
        raise NotImplementedError
