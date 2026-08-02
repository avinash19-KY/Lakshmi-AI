from pathlib import Path

from src.importer.manager import ImportManager
from src.services.profile_service import ProfileService


def test_import_pipeline_loads_sample_csv_and_excel_files() -> None:
    sample_directory = Path(__file__).resolve().parents[1] / "data" / "import_examples"
    service = ProfileService(data_directory=sample_directory)
    service.load_data()

    profile = service.profile_repository.get_all()[0]
    assets = service.asset_repository.get_all()
    liabilities = service.liability_repository.get_all()
    investments = service.investment_repository.get_all()
    goals = service.goal_repository.get_all()

    assert profile.name == "Avinash Kumar"
    assert profile.monthly_income == 160000
    assert len(assets) == 6
    assert liabilities == []
    assert len(investments) == 2
    assert goals[0].name == "Parents' House"


def test_import_manager_loads_excel_file_with_normalized_columns() -> None:
    sample_directory = Path(__file__).resolve().parents[1] / "data" / "import_examples"
    records = ImportManager.load(
        sample_directory / "assets.xlsx",
        required_columns=["name", "category", "value"],
    )

    assert records[0]["name"] == "Emergency fund"
    assert records[0]["category"] == "Cash"
    assert records[0]["value"] == 510000
