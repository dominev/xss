"""Playable snapshots. Add a row here when you freeze a build like DCSS 0.33."""

from pathlib import Path

from tuta import __version__
from tuta.paths import WEB

LOADING_DIR = WEB / "img" / "loading"


def loading_screens() -> list[str]:
    if not LOADING_DIR.exists():
        return []
    return [
        f"/static/img/loading/{p.name}"
        for p in sorted(LOADING_DIR.iterdir())
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ]


def playable() -> list[dict]:
    return [
        {
            "id": "pcls - a0.1",
            "label": "Pocket Crawl Lint Soup α0.1",
            "kind": "release",
            "playable": True,
            "note": "update 20.09.2026",
        },
        {
            "id": "Pocket Crawl Lint Soup - trunk",
            "label": "Test version",
            "kind": "trunk",
            "playable": False,
            "note": "snapshot later",
        },
        {
            "id": "Pocket Crawl Lint Soup - sprint",
            "label": "-_-",
            "kind": "sprint",
            "playable": False,
            "note": "not yet",
        },
    ]


def boot_versions() -> dict:
    return {
        "current": f"Pocket Crawl Lint Soup - α0.1 {__version__}",
        "list": playable(),
        "loading": loading_screens(),
    }
