from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = Path(__file__).resolve().parent
DATA = ROOT / "data"
WEB = ROOT / "web"

SAVES = DATA / "saves"
USERS = DATA / "users.json"
SESSIONS = DATA / "sessions.json"
META = DATA / "meta.json"
MORGUE = DATA / "morgue.json"
SETTINGS = DATA / "settings.json"

DATA.mkdir(parents=True, exist_ok=True)
SAVES.mkdir(parents=True, exist_ok=True)
