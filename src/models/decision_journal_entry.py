from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionJournalEntry:
    """A user-approved note about a financial decision or intention."""

    created_at: str
    note: str
