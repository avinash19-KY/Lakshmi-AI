import csv
from pathlib import Path

from src.services.profile_service import ProfileService


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_profile_service_loads_financial_data_from_csv(tmp_path: Path) -> None:
    write_csv(
        tmp_path / "profile.csv",
        [
            "name",
            "monthly_income",
            "monthly_expenses",
            "monthly_essential_expenses",
            "emergency_fund",
        ],
        [
            {
                "name": "Test User",
                "monthly_income": "100000",
                "monthly_expenses": "70000",
                "monthly_essential_expenses": "60000",
                "emergency_fund": "300000",
            }
        ],
    )
    write_csv(
        tmp_path / "assets.csv",
        ["name", "category", "value"],
        [{"name": "Savings", "category": "Cash", "value": "100000"}],
    )
    write_csv(tmp_path / "liabilities.csv", ["name", "category", "value"], [])
    write_csv(
        tmp_path / "goals.csv",
        ["name", "target_amount", "current_amount"],
        [{"name": "Goal", "target_amount": "500000", "current_amount": "100000"}],
    )

    service = ProfileService(tmp_path)

    assert service.load_profile().name == "Test User"
    assert service.load_assets()[0].value == 100000
    assert service.load_liabilities() == []
    assert service.load_goals()[0].target_amount == 500000
    assert service.load_investments() == []
