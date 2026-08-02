from pathlib import Path

import pytest

from src.services.decision_journal_service import DecisionJournalService


def test_journal_stores_explicit_notes_locally(tmp_path: Path) -> None:
    service = DecisionJournalService(tmp_path / "journal.json")

    entry = service.add("Build emergency reserves before taking new risk.")

    assert entry.note.startswith("Build emergency")
    assert len(service.list_entries()) == 1
    assert service.recent()[0].note == entry.note


def test_journal_rejects_empty_notes(tmp_path: Path) -> None:
    service = DecisionJournalService(tmp_path / "journal.json")

    with pytest.raises(ValueError):
        service.add("   ")


def test_recent_returns_latest_entries(tmp_path: Path) -> None:
    service = DecisionJournalService(tmp_path / "journal.json")
    service.add("First")
    service.add("Second")

    assert [entry.note for entry in service.recent(1)] == ["Second"]
