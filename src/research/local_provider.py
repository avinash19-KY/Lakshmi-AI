from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Optional

from .provider import ResearchProvider, ResearchSnapshot


class LocalResearchProvider:
    """A deterministic local research provider that reads JSON fixtures.

    The fixture is a JSON mapping of instrument_id -> facts, for example:
    {
      "FOO": {
         "name": "Foo Corp",
         "instrument_type": "equity",
         "price": "123.45",
         "historical_annual_return": "0.112",
         "as_of": "2026-07-31",
         "source": "local-fixture",
         "extra": {"sector":"Technology"}
      }
    }

    Prices and returns are parsed as strings into Decimal to ensure deterministic
    numeric semantics.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Research fixture not found: {self.path}")
        with open(self.path, "r", encoding="utf-8") as fh:
            self._data = json.load(fh)

    def get_snapshot(self, instrument_id: str) -> Optional[ResearchSnapshot]:
        raw = self._data.get(instrument_id)
        if not raw:
            return None
        price = None
        if raw.get("price") is not None:
            price = Decimal(str(raw.get("price")))
        hist = None
        if raw.get("historical_annual_return") is not None:
            hist = Decimal(str(raw.get("historical_annual_return")))
        return ResearchSnapshot(
            instrument_id=instrument_id,
            name=raw.get("name"),
            instrument_type=raw.get("instrument_type"),
            price=price,
            historical_annual_return=hist,
            as_of=raw.get("as_of"),
            source=raw.get("source", "local"),
            extra=raw.get("extra"),
        )
