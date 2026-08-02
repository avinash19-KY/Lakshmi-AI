from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List

from src.connectors.base import ConnectorHolding, PortfolioConnector


class LocalSnapshotConnector(PortfolioConnector):
    """Reads a local JSON snapshot file and returns normalized holdings.

    The snapshot file is expected to be a JSON array of objects with fields:
    - external_id (required)
    - name (required)
    - category (required)
    - value (required, numeric)
    - domain (optional, 'investment'|'asset'), defaults to 'investment'
    - as_of (optional ISO-8601 date string)
    """

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def name(self) -> str:
        return f"LocalSnapshot:{self._path.name}"

    def fetch_holdings(self) -> List[ConnectorHolding]:
        if not self._path.exists():
            raise FileNotFoundError(f"Local snapshot not found: {self._path}")

        raw = json.loads(self._path.read_text(encoding="utf-8"))
        total = len(raw) if isinstance(raw, list) else 0
        holdings: List[ConnectorHolding] = []
        for item in raw:
            external_id = item.get("external_id")
            name = item.get("name")
            category = item.get("category")
            value = item.get("value")
            domain = item.get("domain") or "investment"
            as_of_raw = item.get("as_of")
            as_of = None
            if as_of_raw:
                try:
                    as_of = datetime.fromisoformat(as_of_raw)
                except Exception:
                    as_of = None

            if not external_id or not name or category is None or value is None:
                err = ValueError("Malformed snapshot entry: external_id, name, category and value are required")
                setattr(err, "received", total)
                raise err

            try:
                value_num = float(value)
            except Exception:
                err = ValueError(f"Invalid numeric value for external_id={external_id}")
                setattr(err, "received", total)
                raise err

            holdings.append(
                ConnectorHolding(
                    external_id=str(external_id),
                    name=str(name),
                    category=str(category),
                    value=value_num,
                    domain=str(domain),
                    as_of=as_of,
                )
            )

        return holdings
