from dataclasses import dataclass


@dataclass(frozen=True)
class Liability:
    """A financial obligation owed by the user."""

    name: str
    category: str
    value: float
