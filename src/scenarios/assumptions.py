from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Assumption:
    name: str
    value: Decimal
    unit: Optional[str] = None
    source: Optional[str] = None
