"""Morgue and JSON helpers. Keep this file tiny — do not paste pet.py here."""

from __future__ import annotations

import json
from typing import Any

from tuta.paths import MORGUE


def load_json(path, fallback):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            pass
    return fallback


def save_json(path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_morgue() -> list[dict[str, Any]]:
    data = load_json(MORGUE, [])
    return data if isinstance(data, list) else []


def save_morgue(rows: list[dict[str, Any]]) -> None:
    save_json(MORGUE, rows[:80])
