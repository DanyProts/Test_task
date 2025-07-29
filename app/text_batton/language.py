import json
from pathlib import Path
from typing import Any

class Text_get:
    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        file_path = Path(__file__).parent / "text_storage" / "ru.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def t(self, key: str, **kwargs) -> str:
        text = self._data.get(key, key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

text_get = Text_get()
