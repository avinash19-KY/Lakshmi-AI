from __future__ import annotations

from typing import Any

from src.models.asset import Asset
from src.models.financial_goal import FinancialGoal
from src.models.financial_profile import FinancialProfile
from src.models.investment import Investment
from src.models.liability import Liability


class Mapper:
    """Maps normalized records to canonical field names."""

    def __init__(self, field_mapping: dict[str, str] | None = None) -> None:
        self._field_mapping = field_mapping or {}

    def map(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self._field_mapping:
            return records

        return [self._map_record(record) for record in records]

    def _map_record(self, record: dict[str, Any]) -> dict[str, Any]:
        mapped_record: dict[str, Any] = {}
        for key, value in record.items():
            mapped_key = self._field_mapping.get(key, key)
            mapped_record[mapped_key] = value
        return mapped_record


class AssetMapper:
    """Converts normalized dictionaries into Asset domain objects."""

    def map(self, record: dict[str, Any]) -> Asset:
        return Asset(
            name=str(record["name"]),
            category=str(record["category"]),
            value=float(record["value"]),
        )

    def map_all(self, records: list[dict[str, Any]]) -> list[Asset]:
        return [self.map(record) for record in records]


class LiabilityMapper:
    """Converts normalized dictionaries into Liability domain objects."""

    def map(self, record: dict[str, Any]) -> Liability:
        return Liability(
            name=str(record["name"]),
            category=str(record["category"]),
            value=float(record["value"]),
        )

    def map_all(self, records: list[dict[str, Any]]) -> list[Liability]:
        return [self.map(record) for record in records]


class InvestmentMapper:
    """Converts normalized dictionaries into Investment domain objects."""

    def map(self, record: dict[str, Any]) -> Investment:
        return Investment(
            name=str(record["name"]),
            category=str(record["category"]),
            value=float(record["value"]),
        )

    def map_all(self, records: list[dict[str, Any]]) -> list[Investment]:
        return [self.map(record) for record in records]


class GoalMapper:
    """Converts normalized dictionaries into FinancialGoal domain objects."""

    def map(self, record: dict[str, Any]) -> FinancialGoal:
        return FinancialGoal(
            name=str(record["name"]),
            target_amount=float(record["target_amount"]),
            current_amount=float(record["current_amount"]),
        )

    def map_all(self, records: list[dict[str, Any]]) -> list[FinancialGoal]:
        return [self.map(record) for record in records]


class ProfileMapper:
    """Converts normalized dictionaries into FinancialProfile domain objects."""

    def map(self, record: dict[str, Any]) -> FinancialProfile:
        return FinancialProfile(
            name=str(record["name"]),
            monthly_income=float(record["monthly_income"]),
            monthly_expenses=float(record["monthly_expenses"]),
            monthly_essential_expenses=float(record["monthly_essential_expenses"]),
            emergency_fund=float(record["emergency_fund"]),
        )

    def map_all(self, records: list[dict[str, Any]]) -> list[FinancialProfile]:
        return [self.map(record) for record in records]
