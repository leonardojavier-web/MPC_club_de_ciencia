import json
from pathlib import Path
from typing import Any


class JsonHistoryRepository:
    """Reads the historical records from the shared JSON source."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        self._file_path = Path(file_path) if file_path else Path(__file__).with_name("fundacion.json")

    def get_records(self) -> list[dict[str, Any]] | None:
        if not self._file_path.exists():
            return None
        with self._file_path.open("r", encoding="utf-8") as file:
            return json.load(file)