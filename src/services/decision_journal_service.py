import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.models.decision_journal_entry import DecisionJournalEntry


class DecisionJournalService:
    """Store explicitly requested decision notes in a local JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def add(self, note: str) -> DecisionJournalEntry:
        cleaned_note = note.strip()
        if not cleaned_note:
            raise ValueError("A journal note cannot be empty.")

        entry = DecisionJournalEntry(
            created_at=datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
            note=cleaned_note,
        )
        entries = self.list_entries()
        entries.append(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([asdict(item) for item in entries], indent=2),
            encoding="utf-8",
        )
        return entry

    def list_entries(self) -> list[DecisionJournalEntry]:
        if not self.path.exists():
            return []

        raw_entries = json.loads(self.path.read_text(encoding="utf-8"))
        return [DecisionJournalEntry(**entry) for entry in raw_entries]

    def recent(self, limit: int = 5) -> list[DecisionJournalEntry]:
        if limit <= 0:
            return []
        return self.list_entries()[-limit:]
