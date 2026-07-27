from __future__ import annotations

from pathlib import Path


class ImportFrameworkError(Exception):
    """Base exception for import framework failures."""


class FileMissingError(ImportFrameworkError, FileNotFoundError):
    """Raised when the import file cannot be found."""


class FileTypeNotSupportedError(ImportFrameworkError, ValueError):
    """Raised when the import file does not use a supported extension."""


class RequiredColumnsMissingError(ImportFrameworkError, ValueError):
    """Raised when the file does not contain required columns."""

    def __init__(self, required_columns: list[str], missing_columns: list[str], file_path: Path) -> None:
        self.required_columns = required_columns
        self.missing_columns = missing_columns
        self.file_path = file_path
        message = (
            f"File {file_path} is missing required columns: {', '.join(missing_columns)}. "
            f"Expected: {', '.join(required_columns)}."
        )
        super().__init__(message)
