from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.importer.manager import ImportManager
from src.importer.mappers import (
    AssetMapper,
    GoalMapper,
    InvestmentMapper,
    LiabilityMapper,
    ProfileMapper,
)
from src.models.asset import Asset
from src.models.financial_goal import FinancialGoal
from src.models.financial_profile import FinancialProfile
from src.models.investment import Investment
from src.models.liability import Liability
from src.repositories.asset_repository import AssetRepository
from src.repositories.financial_profile_repository import FinancialProfileRepository
from src.repositories.goal_repository import GoalRepository
from src.repositories.investment_repository import InvestmentRepository
from src.repositories.liability_repository import LiabilityRepository


class ProfileService:
    """Loads the personal MVP's financial data from local files."""

    def __init__(
        self,
        data_directory: Optional[Path] = None,
        asset_mapper: AssetMapper | None = None,
        liability_mapper: LiabilityMapper | None = None,
        investment_mapper: InvestmentMapper | None = None,
        goal_mapper: GoalMapper | None = None,
        profile_mapper: ProfileMapper | None = None,
        asset_repository: AssetRepository | None = None,
        liability_repository: LiabilityRepository | None = None,
        investment_repository: InvestmentRepository | None = None,
        goal_repository: GoalRepository | None = None,
        profile_repository: FinancialProfileRepository | None = None,
    ) -> None:
        project_root = Path(__file__).resolve().parents[2]
        self.data_directory = data_directory or project_root / "data"
        self._asset_mapper = asset_mapper or AssetMapper()
        self._liability_mapper = liability_mapper or LiabilityMapper()
        self._investment_mapper = investment_mapper or InvestmentMapper()
        self._goal_mapper = goal_mapper or GoalMapper()
        self._profile_mapper = profile_mapper or ProfileMapper()
        self.asset_repository = asset_repository or AssetRepository()
        self.liability_repository = liability_repository or LiabilityRepository()
        self.investment_repository = investment_repository or InvestmentRepository()
        self.goal_repository = goal_repository or GoalRepository()
        self.profile_repository = profile_repository or FinancialProfileRepository()

    def load_data(self) -> None:
        """Loads all financial data into the configured repositories."""
        self.profile_repository.clear()
        self.asset_repository.clear()
        self.liability_repository.clear()
        self.investment_repository.clear()
        self.goal_repository.clear()

        self._load_profile()
        self._load_assets()
        self._load_liabilities()
        self._load_investments()
        self._load_goals()

    def load_profile(self) -> FinancialProfile:
        if not self.profile_repository.count():
            self.load_data()

        profiles = self.profile_repository.get_all()
        if not profiles:
            raise ValueError("profile.csv must contain one financial profile.")

        return profiles[0]

    def load_assets(self) -> list[Asset]:
        if not self.asset_repository.count():
            self.load_data()

        return self.asset_repository.get_all()

    def load_liabilities(self) -> list[Liability]:
        if not self.liability_repository.count():
            self.load_data()

        return self.liability_repository.get_all()

    def load_goals(self) -> list[FinancialGoal]:
        if not self.goal_repository.count():
            self.load_data()

        return self.goal_repository.get_all()

    def load_investments(self) -> list[Investment]:
        if not self.investment_repository.count():
            self.load_data()

        return self.investment_repository.get_all()

    def _load_profile(self) -> None:
        rows = self._read_rows(
            "profile",
            required_columns=[
                "name",
                "monthly_income",
                "monthly_expenses",
                "monthly_essential_expenses",
                "emergency_fund",
            ],
        )
        if not rows:
            raise ValueError("profile.csv must contain one financial profile.")

        self.profile_repository.add(self._profile_mapper.map(rows[0]))

    def _load_assets(self) -> None:
        rows = self._read_rows(
            "assets",
            required_columns=["name", "category", "value"],
        )
        self.asset_repository.add_many(self._asset_mapper.map_all(rows))

    def _load_liabilities(self) -> None:
        rows = self._read_rows(
            "liabilities",
            required_columns=["name", "category", "value"],
        )
        self.liability_repository.add_many(self._liability_mapper.map_all(rows))

    def _load_investments(self) -> None:
        try:
            rows = self._read_rows(
                "investments",
                required_columns=["name", "category", "value"],
            )
        except FileNotFoundError:
            return

        self.investment_repository.add_many(self._investment_mapper.map_all(rows))

    def _load_goals(self) -> None:
        rows = self._read_rows(
            "goals",
            required_columns=["name", "target_amount", "current_amount"],
        )
        self.goal_repository.add_many(self._goal_mapper.map_all(rows))

    def _resolve_source_file(self, filename: str) -> Path:
        candidate = self.data_directory / filename
        if candidate.suffix:
            if candidate.exists():
                return candidate
            raise FileNotFoundError(f"Import file not found: {candidate}")

        for extension in [".csv", ".xlsx"]:
            candidate = self.data_directory / f"{filename}{extension}"
            if candidate.exists():
                return candidate

        raise FileNotFoundError(
            f"Import file not found for base name '{filename}'. "
            "Supported names are '*.csv' or '*.xlsx'."
        )

    def _read_rows(
        self,
        filename: str,
        required_columns: list[str] | None = None,
    ) -> list[dict[str, object]]:
        file_path = self._resolve_source_file(filename)
        return ImportManager.load(file_path, required_columns=required_columns)
