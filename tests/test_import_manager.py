import csv
from datetime import date
from pathlib import Path

import pytest
from openpyxl import Workbook

from src.importer.exceptions import RequiredColumnsMissingError
from src.importer.manager import ImportManager


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(fieldnames)
    for row in rows:
        worksheet.append([row.get(field, None) for field in fieldnames])
    workbook.save(path)


def test_import_manager_loads_csv_records(tmp_path: Path) -> None:
    write_csv(
        tmp_path / "assets.csv",
        ["Asset Name", "Category", "Value", "Purchase Date"],
        [
            {
                "Asset Name": "Savings Account",
                "Category": "Cash",
                "Value": "250000",
                "Purchase Date": "2025-12-31",
            }
        ],
    )

    records = ImportManager.load(tmp_path / "assets.csv")

    assert records == [
        {
            "asset_name": "Savings Account",
            "category": "Cash",
            "value": 250000,
            "purchase_date": date(2025, 12, 31),
        }
    ]


def test_import_manager_loads_xlsx_records(tmp_path: Path) -> None:
    write_xlsx(
        tmp_path / "assets.xlsx",
        ["Asset Name", "Category", "Value"],
        [
            {
                "Asset Name": "Fixed Deposit",
                "Category": "Cash",
                "Value": "150000",
            }
        ],
    )

    records = ImportManager.load(tmp_path / "assets.xlsx")

    assert records == [
        {
            "asset_name": "Fixed Deposit",
            "category": "Cash",
            "value": 150000,
        }
    ]


def test_import_manager_raises_when_required_columns_are_missing(tmp_path: Path) -> None:
    write_csv(
        tmp_path / "assets.csv",
        ["Name", "Value"],
        [{"Name": "Cash", "Value": "50000"}],
    )

    with pytest.raises(RequiredColumnsMissingError, match="missing required columns"):
        ImportManager.load(
            tmp_path / "assets.csv",
            required_columns=["name", "value", "category"],
        )
