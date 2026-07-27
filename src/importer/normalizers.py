from __future__ import annotations

import re
from datetime import datetime, date, time
from typing import Any


class Normalizer:
    """Converts raw records into normalized records."""

    _COLUMN_NAME_PATTERN = re.compile(r"[^a-z0-9]+")
    _INTEGER_PATTERN = re.compile(r"^-?\d+$")
    _FLOAT_PATTERN = re.compile(r"^-?\d+(?:\.\d+)?$")
    _DATE_FORMATS = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d %b %Y",
        "%d %B %Y",
    ]

    def normalize_records(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self._normalize_record(record) for record in records]

    def _normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        normalized_record: dict[str, Any] = {}
        for key, value in record.items():
            normalized_key = self._normalize_column_name(key)
            normalized_record[normalized_key] = self._normalize_value(value)
        return normalized_record

    def _normalize_column_name(self, column_name: Any) -> str:
        normalized = str(column_name or "").strip().lower()
        normalized = self._COLUMN_NAME_PATTERN.sub("_", normalized)
        normalized = normalized.strip("_")
        return normalized

    def _normalize_value(self, value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return value

        if isinstance(value, (datetime, date, time)):
            return value

        cleaned_value = str(value).strip()
        if cleaned_value == "":
            return None

        number = self._parse_number(cleaned_value)
        if number is not None:
            return number

        date_value = self._parse_date(cleaned_value)
        if date_value is not None:
            return date_value

        return cleaned_value

    def _parse_number(self, raw_value: str) -> int | float | None:
        normalized = raw_value.replace(",", "").replace("_", "")
        if self._INTEGER_PATTERN.fullmatch(normalized):
            try:
                return int(normalized)
            except ValueError:
                return None

        if self._FLOAT_PATTERN.fullmatch(normalized):
            try:
                return float(normalized)
            except ValueError:
                return None

        return None

    def _parse_date(self, raw_value: str) -> date | datetime | None:
        iso_value = raw_value.replace(" ", "T")
        try:
            parsed = datetime.fromisoformat(iso_value)
            return parsed.date() if parsed.time() == time(0, 0) else parsed
        except ValueError:
            pass

        for date_format in self._DATE_FORMATS:
            try:
                parsed = datetime.strptime(raw_value, date_format)
                return parsed.date()
            except ValueError:
                continue

        return None
