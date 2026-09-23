"""Оставлено для доделки, многопользовательская составляющая. Заглушка - admin / admin."""

from __future__ import annotations

import json
import secrets
from datetime import datetime
from typing import Any

from tuta.paths import SESSIONS, USERS

DEFAULT_USERS = {
    "admin": {"password": "admin", "role": "op", "created": "2026-09-20"},
}


def _read(path, fallback):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            pass
    return fallback


def _write(path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def users() -> dict[str, Any]:
    data = _read(USERS, None)
    if not data:
        _write(USERS, DEFAULT_USERS)
        return dict(DEFAULT_USERS)
    return data


def sessions() -> dict[str, Any]:
    return _read(SESSIONS, {})


def login(username: str, password: str) -> dict[str, Any] | None:
    name = (username or "").strip()
    book = users()
    rec = book.get(name)
    if not rec or rec.get("password") != password:
        return None
    token = secrets.token_hex(16)
    bag = sessions()
    bag[token] = {"user": name, "role": rec.get("role", "player"), "at": datetime.now().isoformat(timespec="seconds")}
    _write(SESSIONS, bag)
    return {"token": token, "user": name, "role": rec.get("role", "player")}


def resolve(token: str | None) -> dict[str, Any] | None:
    if not token:
        return None
    return sessions().get(token)


def register_stub() -> dict[str, str]:
    return {"ok": False, "error": "регистрация откроется вместе с сетевыми забегами"}
