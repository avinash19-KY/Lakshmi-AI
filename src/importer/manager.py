from __future__ import annotations

from pathlib import Path
from typing import Any

from src.importer.exceptions import ImportFrameworkError
from src.importer.mappers import Mapper
from src.importer.normalizers import Normalizer
from src.importer.readers import CsvReader, ExcelReader, Reader
from src.importer.repositories import InMemoryRepository, Repository
from src.importer.validators import FileValidator


class ImportManager:
    """Orchestrates import file processing and returns normalized records."""

    _READERS: dict[str, type[Reader]] = {
        ".csv": CsvReader,
        ".xlsx": ExcelReader,
    }

    def __init__(
        self,
        validator: FileValidator | None = None,
        normalizer: Normalizer | None = None,
        mapper: Mapper | None = None,
        repository: Repository | None = None,
    ) -> None:
        self._validator = validator or FileValidator()
        self._normalizer = normalizer or Normalizer()
        self._mapper = mapper or Mapper()
        self._repository = repository or InMemoryRepository()

    @classmethod
    def load(
        cls,
        file_path: str | Path,
        required_columns: list[str] | None = None,
        field_mapping: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        manager = cls(mapper=Mapper(field_mapping))
        return manager._load(Path(file_path), required_columns)

    def _load(
        self,
        file_path: Path,
        required_columns: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        self._validator.validate(file_path, required_columns=required_columns)
        reader = self._resolve_reader(file_path)
        raw_records = reader.read(file_path)
        normalized_records = self._normalizer.normalize_records(raw_records)
        mapped_records = self._mapper.map(normalized_records)
        self._repository.save(mapped_records)
        return self._repository.retrieve()

    def _resolve_reader(self, file_path: Path) -> Reader:
        reader_class = self._READERS.get(file_path.suffix.lower())
        if reader_class is None:
            raise ImportFrameworkError(
                f"Unable to resolve a reader for extension '{file_path.suffix}'."
            )
        return reader_class()
