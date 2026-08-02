from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.scenarios.assumptions import Assumption


@dataclass(frozen=True)
class ScenarioResult:
    scenario_type: str
    inputs: Dict[str, Any]
    assumptions: List[Assumption]
    outputs: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class TimePoint:
    year: int
    contributions: Decimal
    growth: Decimal
    ending_value: Decimal
