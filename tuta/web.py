"""HTTP app: CAO lobby + game API."""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from tuta import __version__
from tuta.auth import login as do_login
from tuta.auth import register_stub, resolve
from tuta.catalog import catalog, char_code
from tuta.lore import NEWS, SLIDES
from tuta.paths import WEB
from tuta.versions import boot_versions
from tuta.pet import RELICS, SPECIES, TEMPER_MODS, load_meta, save_meta
from tuta.store import load_morgue, save_morgue

app = FastAPI(title="Pocket Crawl Lint Soup α0.1", version=__version__)
app.mount("/static", StaticFiles(directory=WEB), name="static")


def _user(authorization: str | None) -> dict | None:
    token = ""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    return resolve(token)


def board_rows() -> list[dict[str, Any]]:
    rows = []
    for rec in load_morgue():
        rows.append(
            {
                "user": rec.get("name") or "anon",
                "game": "pcls - α0.1",
                "xl": rec.get("xl", 1),
                "char": char_code(rec.get("species", "zhar"), rec.get("temper_key") or "snark"),
                "place": rec.get("place", "D:1"),
                "turn": rec.get("kills", 0) * 40 + rec.get("xl", 1) * 10,
                "time": _fmt(rec.get("time_s", 0)),
                "god": rec.get("relic") or "none",
                "idle": "" if rec.get("result") != "dead" else "",
                "specs": "",
                "milestone": rec.get("milestone") or "",
                "result": rec.get("result"),
            }
        )
    return rows


def _fmt(s: int) -> str:
    s = int(s or 0)
    if s >= 3600:
        return f"{s // 3600}h {s % 3600 // 60}m"
    if s >= 60:
        return f"{s // 60}m"
    return f"{s}s"


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB / "index.html")


@app.get("/api/boot")
async def boot(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    meta = load_meta()
    meta.setdefault("seen_lore", False)
    return {
        "ok": True,
        "version": __version__,
        "user": _user(authorization),
        "meta": meta,
        "morgue": load_morgue(),
        "board": board_rows(),
        "news": NEWS,
        "catalog": catalog(),
        "lore": SLIDES,
        "versions": boot_versions(),
    }


class LoginIn(BaseModel):
    username: str = ""
    password: str = ""


@app.post("/api/login")
async def login(body: LoginIn) -> dict[str, Any]:
    got = do_login(body.username, body.password)
    if not got:
        return {"ok": False, "error": "Login incorrect."}
    return {"ok": True, **got}


@app.post("/api/register")
async def register() -> dict[str, Any]:
    return register_stub()


class SeenLore(BaseModel):
    seen: bool = True


@app.post("/api/seen-lore")
async def seen_lore(_: SeenLore) -> dict[str, Any]:
    meta = load_meta()
    meta["seen_lore"] = True
    save_meta(meta)
    return {"ok": True}


class RunEnd(BaseModel):
    name: str = "без имени"
    species: str = "zhar"
    temper: str = "snark"
    xl: int = 1
    place: str = "D:1"
    time_s: int = 0
    kills: int = 0
    result: str = "dead"
    killed_by: str = ""
    milestone: str = ""
    relic_id: str | None = None


@app.post("/api/run-end")
async def run_end(body: RunEnd, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    who = _user(authorization)
    uname = (who or {}).get("user") or body.name
    meta = load_meta()
    meta["runs"] = int(meta.get("runs", 0)) + 1
    meta["best_level"] = max(int(meta.get("best_level", 1)), body.xl)
    meta["best_place"] = body.place
    drop = body.relic_id if body.relic_id in RELICS else random.choice(list(RELICS.keys()))
    unlocked = list(meta.get("relics") or [])
    if body.result == "dead" and drop not in unlocked:
        unlocked.append(drop)
        meta["relics"] = unlocked
    if body.result == "win":
        meta["shards"] = int(meta.get("shards", 0)) + 1
    save_meta(meta)
    info = SPECIES.get(body.species, SPECIES["zhar"])
    row = {
        "id": meta["runs"],
        "when": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user": uname,
        "name": body.name[:24],
        "species": body.species,
        "title": info["title"],
        "temper": TEMPER_MODS.get(body.temper, {}).get("label", body.temper),
        "temper_key": body.temper,
        "xl": body.xl,
        "place": body.place,
        "time_s": body.time_s,
        "kills": body.kills,
        "result": body.result,
        "killed_by": body.killed_by,
        "milestone": body.milestone or ("found the D:1 stair" if body.result == "win" else "died on D:1"),
        "relic": RELICS.get(drop, {}).get("name", drop),
        "relic_id": drop,
    }
    rows = load_morgue()
    rows.insert(0, row)
    save_morgue(rows)
    return {"ok": True, "row": row, "meta": meta, "board": board_rows()}