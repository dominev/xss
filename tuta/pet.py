"""Pet model, species, saves, settings — Pocket Crawl Lint Soup α0.1"""

from __future__ import annotations

import json
import random
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
SAVES_DIR = DATA / "saves"
SETTINGS_PATH = DATA / "settings.json"
META_PATH = DATA / "meta.json"
OLD_SAVE = ROOT / "pet_save.json"

SAVES_DIR.mkdir(exist_ok=True)

Stage = Literal["яйцо", "малыш", "подросток", "взрослый", "легенда"]
MoodName = Literal["восторженный", "нормальный", "печальный", "злой", "мертв внутри"]
SpeciesId = Literal["zhar", "sashochek", "morok"]
Temperament = Literal["мягкий", "занудный", "токсик"]
StartCare = Literal["сытый", "нормальный", "заброшенный питомец"]

TICK_SECONDS = 1

PASSIVE_AGGRO = {
    "feed": [
        "О, вспомнил. Герой трудового дня.",
        "Спасибо, конечно. Я уже почти привык голодать.",
        "Еда. Как оригинально. А разговаривать будем?",
        "Ну хоть не отравленное. Наверное.",
    ],
    "ignore": [
        "Ничего, я тут. Просто существую. Без тебя тоже можно.",
        "Забавно. Меня снова нет в твоих приоритетах.",
        "Круто. Я запишу это в дневник. Снова.",
        "Не переживай, я сам себя поглажу. Как-нибудь.",
    ],
    "play": [
        "Игра? В это время суток? Смело.",
        "Ладно. Только не делай вид, что это забота.",
        "Я выиграл. Как всегда. Ты просто присутствовал.",
    ],
    "sick": [
        "Мне плохо. Но ты занят, я понимаю.",
        "Температура есть. Внимания нет. Классика.",
        "Если я исчезну — это не баг. Это последствия.",
    ],
    "idle": [
        "Скучно. Даже злиться уже лень.",
        "Я эволюционирую из злости. Запиши.",
        "Ты моргнул. Я заметил. И осудил.",
        "Журнал событий заполняется сам. Угадай чем.",
    ],
}

TYPE_CHART = {
    "огонь": {"огонь": 0.5, "вода": 0.5, "тень": 1.5},
    "вода": {"огонь": 1.5, "вода": 0.5, "тень": 1.0},
    "тень": {"огонь": 1.0, "вода": 1.5, "тень": 0.5},
}

SPECIES: dict[str, dict] = {
    "zhar": {
        "title": "Жарёк",
        "type": "огненный",
        "blurb": "Быстро голодает, перекорм обжигает, болеет реже.",
        "palette": {
            ".": None,
            "0": "#2a1208",
            "1": "#f08a2a",
            "2": "#c45c14",
            "3": "#1a0a04",
            "4": "#ffe56a",
            "5": "#ff5a2a",
        },
        "mods": {
            "hunger_decay": 1.45,
            "mood_decay": 1.0,
            "health_decay": 1.0,
            "play_mood": 1.5,
            "feed_hunger": 1.0,
            "overfeed_dmg": 1.7,
            "ignore_mood": 1.1,
            "sick_chance": 0.55,
            "heal": 0.9,
            "idle_talk": 1.0,
            "spite_evo": 1.0,
        },
        "frames": {
            "idle": [
                [
                    "....44....",
                    "...4554...",
                    "..011110..",
                    ".01111110.",
                    ".01122110.",
                    ".01311310.",
                    ".01111110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ],
                [
                    ".....44...",
                    "....4554..",
                    "..011110..",
                    ".01111110.",
                    ".01122110.",
                    ".01311310.",
                    ".01111110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ],
            ],
            "happy": [
                [
                    "....44....",
                    "...4554...",
                    "..011110..",
                    ".01111110.",
                    ".01522510.",
                    ".01.33.10.",
                    ".01155110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ]
            ],
            "angry": [
                [
                    "....55....",
                    "...5445...",
                    "..011110..",
                    ".01111110.",
                    ".01233210.",
                    ".01311310.",
                    ".01100110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ]
            ],
            "sick": [
                [
                    "....44....",
                    "..........",
                    "..011110..",
                    ".01111110.",
                    ".01122110.",
                    ".01-33-10.",
                    ".01111110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ]
            ],
            "dead": [
                [
                    "..........",
                    "..........",
                    "..011110..",
                    ".01111110.",
                    ".01122110.",
                    ".01x33x10.",
                    ".01111110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ]
            ],
        },
    },
    "Топь": {
        "title": "Топь",
        "type": "водный",
        "blurb": "Здоровье и сытость держится дольше, игнор сушит настроение, лечится охотнее.",
        "palette": {
            ".": None,
            "0": "#062430",
            "1": "#3ec6d8",
            "2": "#1a7f96",
            "3": "#04151c",
            "4": "#b8f3ff",
            "5": "#7ee0a8",
        },
        "mods": {
            "hunger_decay": 0.7,
            "mood_decay": 1.05,
            "health_decay": 0.6,
            "play_mood": 1.1,
            "feed_hunger": 1.15,
            "overfeed_dmg": 0.7,
            "ignore_mood": 1.45,
            "sick_chance": 0.9,
            "heal": 1.35,
            "idle_talk": 0.85,
            "spite_evo": 0.9,
        },
        "frames": {
            "idle": [
                [
                    "....44....",
                    "...4114...",
                    "..411114..",
                    ".01111110.",
                    ".01122110.",
                    ".01311310.",
                    ".01111110.",
                    "..011110..",
                    "...2222...",
                    "....00....",
                ],
                [
                    ".....44...",
                    "....4114..",
                    "..411114..",
                    ".01111110.",
                    ".01122110.",
                    ".01311310.",
                    ".01111110.",
                    "..011110..",
                    "...2222...",
                    "....00....",
                ],
            ],
            "happy": [
                [
                    "....44....",
                    "...4114...",
                    "..411114..",
                    ".01111110.",
                    ".01522510.",
                    ".01.33.10.",
                    ".01155110.",
                    "..011110..",
                    "...2222...",
                    "....00....",
                ]
            ],
            "angry": [
                [
                    "....44....",
                    "...4114...",
                    "..411114..",
                    ".01111110.",
                    ".01233210.",
                    ".01311310.",
                    ".01100110.",
                    "..011110..",
                    "...2222...",
                    "....00....",
                ]
            ],
            "sick": [
                [
                    "....44....",
                    "...4114...",
                    "..411114..",
                    ".01111110.",
                    ".01122110.",
                    ".01433410.",
                    ".01111110.",
                    "..011110..",
                    "...2222...",
                    "....00....",
                ]
            ],
            "dead": [
                [
                    "..........",
                    "...4114...",
                    "..411114..",
                    ".01111110.",
                    ".01122110.",
                    ".01x33x10.",
                    ".01111110.",
                    "..011110..",
                    "...2222...",
                    "....00....",
                ]
            ],
        },
    },
    "morok": {
        "title": "Морок",
        "type": "теневой",
        "blurb": "Игнор почти не ранит, молчит реже, злобным растет быстрее, играть не любит.",
        "palette": {
            ".": None,
            "0": "#14081c",
            "1": "#6b4aa8",
            "2": "#3b2468",
            "3": "#f2e38a",
            "4": "#c9b6ff",
            "5": "#ff7ad1",
        },
        "mods": {
            "hunger_decay": 1.0,
            "mood_decay": 0.85,
            "health_decay": 1.1,
            "play_mood": 0.65,
            "feed_hunger": 0.95,
            "overfeed_dmg": 1.0,
            "ignore_mood": 0.45,
            "sick_chance": 1.15,
            "heal": 1.0,
            "idle_talk": 1.8,
            "spite_evo": 1.6,
        },
        "frames": {
            "idle": [
                [
                    "..4....4..",
                    ".040..040.",
                    "..011110..",
                    ".01111110.",
                    ".01222110.",
                    ".01311110.",
                    ".01111110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ],
                [
                    ".4......4.",
                    ".040..040.",
                    "..011110..",
                    ".01111110.",
                    ".01222110.",
                    ".01113110.",
                    ".01111110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ],
            ],
            "happy": [
                [
                    "..4....4..",
                    ".040..040.",
                    "..011110..",
                    ".01111110.",
                    ".01522510.",
                    ".01.3.310.",
                    ".01155110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ]
            ],
            "angry": [
                [
                    "..5....5..",
                    ".050..050.",
                    "..011110..",
                    ".01111110.",
                    ".01333110.",
                    ".01311110.",
                    ".01100110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ]
            ],
            "sick": [
                [
                    "..4....4..",
                    "..........",
                    "..011110..",
                    ".01111110.",
                    ".01222110.",
                    ".01433110.",
                    ".01111110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ]
            ],
            "dead": [
                [
                    "..........",
                    "..........",
                    "..011110..",
                    ".01111110.",
                    ".01222110.",
                    ".01x3x310.",
                    ".01111110.",
                    "..011110..",
                    "..022220..",
                    "...0..0...",
                ]
            ],
        },
    },
}

TEMPER_MODS = {
    "soft": {"mood_hits": 0.7, "talk": 0.7, "label": "Мягкий"},
    "snark": {"mood_hits": 1.0, "talk": 1.0, "label": "Язвительный"},
    "venom": {"mood_hits": 1.35, "talk": 1.4, "label": "Ядовитый"},
}

START_STATS = {
    "fed": {"hunger": 82, "mood": 74, "health": 88, "label": "Легкий (сразу сытый)"},
    "normal": {"hunger": 55, "mood": 60, "health": 80, "label": "Нормальный (стабильный)"},
    "abandoned": {"hunger": 28, "mood": 32, "health": 58, "label": "Заброшенный"},
}

LEVEL_XP = {1: 40, 2: 80, 3: 140, 4: 220, 5: 320, 6: 9999}
LEVEL_STAGE: dict[int, Stage] = {
    1: "яйцо",
    2: "малыш",
    3: "подросток",
    4: "взрослый",
    5: "легенда",
    6: "легенда",
}

SHOP: dict[str, dict] = {
    "crumb": {
        "name": "Сухарь",
        "price": 55,
        "kind": "consumable",
        "icon": "🍞",
        "desc": "+18 голода",
        "effect": {"hunger": 18, "xp": 2},
    },
    "jelly": {
        "name": "Желе настроения",
        "price": 70,
        "kind": "consumable",
        "icon": "🫐",
        "desc": "+16 настроения",
        "effect": {"mood": 16, "xp": 2},
    },
    "patch": {
        "name": "Пластырь",
        "price": 90,
        "kind": "consumable",
        "icon": "🩹",
        "desc": "+20 здоровья, шанс снять болезнь",
        "effect": {"health": 20, "cure": True, "xp": 3},
    },
    "spice": {
        "name": "Острый уголёк",
        "price": 110,
        "kind": "consumable",
        "icon": "🌶️",
        "desc": "Жарёку вкусно. Остальным — на свой страх.",
        "effect": {"hunger": 10, "mood": 8},
        "prefer": "zhar",
    },
    "ribbon": {
        "name": "Бант",
        "price": 260,
        "kind": "cosmetic",
        "icon": "🎀",
        "desc": "На голове. Сдерживает падение настроения.",
        "mods": {"mood_decay": 0.8},
    },
    "collar": {
        "name": "Ошейник с колокольчиком",
        "price": 340,
        "kind": "cosmetic",
        "icon": "🔔",
        "desc": "На шее. Игнор бьёт слабее.",
        "mods": {"ignore_mood": 0.75},
    },
    "amulet": {
        "name": "Тута-амулет",
        "price": 520,
        "kind": "cosmetic",
        "icon": "🧿",
        "desc": "На груди. Здоровье тает медленнее.",
        "mods": {"health_decay": 0.7, "sick_chance": 0.7},
    },
}

# 10x10 overlays, same alphabet as sprites: 6 pink, 7 gold, 8 teal, 9 white
OVERLAYS: dict[str, dict] = {
    "ribbon": {
        "palette": {"6": "#ff6b9a", "9": "#ffe6ef", "7": "#c81e5c"},
        "grid": [
            "..66..66..",
            ".69966996.",
            "..766667..",
            "....77....",
            "..........",
            "..........",
            "..........",
            "..........",
            "..........",
            "..........",
        ],
    },
    "collar": {
        "palette": {"7": "#f0c14b", "0": "#2a1a08", "9": "#fff3b0"},
        "grid": [
            "..........",
            "..........",
            "..........",
            "..........",
            "..........",
            "..........",
            "...00000..",
            "..0.7.9.0.",
            "...00000..",
            "..........",
        ],
    },
    "amulet": {
        "palette": {"8": "#3ec6d8", "4": "#b8f3ff", "0": "#062430"},
        "grid": [
            "..........",
            "..........",
            "..........",
            "..........",
            "..........",
            "....00....",
            "....48....",
            "....84....",
            "..........",
            "..........",
        ],
    },
}


RELICS: dict[str, dict] = {
    "warm_core": {
        "name": "Тёплое ядро",
        "icon": "🔥",
        "desc": "Следующий забег: голод тает медленнее.",
        "mods": {"hunger_decay": 0.65},
    },
    "quiet_bell": {
        "name": "Тихий колокол",
        "icon": "🔕",
        "desc": "Игнор почти не ранит. Ты уже тренировался.",
        "mods": {"ignore_mood": 0.5},
    },
    "fat_wallet": {
        "name": "Жирный кошелёк",
        "icon": "💰",
        "desc": "Старт +40₮. Клики дают 2₮.",
        "start_coins": 40,
        "click": 2,
    },
    "second_chance": {
        "name": "Второй шанс",
        "icon": "🩹",
        "desc": "Один раз за забег здоровье не падает ниже 15.",
        "floor_once": 15,
    },
    "legend_seed": {
        "name": "Семя легенды",
        "icon": "🌱",
        "desc": "Старт с 25 XP. Ближе к малышу.",
        "start_xp": 25,
    },
}


def load_meta() -> dict:
    if META_PATH.exists():
        try:
            return json.loads(META_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            pass
    return {"shards": 0, "relics": [], "runs": 0, "best_level": 1}


def save_meta(meta: dict) -> None:
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def now_stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def slugify(name: str) -> str:
    base = re.sub(r"[^\wа-яА-ЯёЁ]+", "_", name.strip(), flags=re.UNICODE)
    base = base.strip("_") or "pet"
    return f"{base[:24]}_{datetime.now().strftime('%m%d_%H%M')}_{uuid.uuid4().hex[:4]}"


def type_multiplier(attack: str, defend: str) -> float:
    return TYPE_CHART.get(attack, {}).get(defend, 1.0)


def emotion_for(pet: "Pet") -> str:
    if not pet.alive:
        return "dead"
    if pet.sick:
        return "sick"
    if pet.mood >= 75:
        return "happy"
    if pet.mood < 30:
        return "angry"
    return "idle"


THEME_KEYS = {"Темная": "dark", "Светлая": "light", "Системная": "oled", "dark": "dark", "light": "light", "oled": "oled"}
ACCENT_KEYS = {"Зеленый": "green", "Оранжевый": "orange", "Фиолетовый": "violet", "green": "green", "orange": "orange", "violet": "violet"}


@dataclass
class Settings:
    theme: str = "dark"
    accent: str = "green"
    immortal: bool = False
    reduce_motion: bool = False
    show_journal: bool = True
    tick_seconds: int = 1

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> "Settings":
        known = {k: data[k] for k in cls.__dataclass_fields__ if k in data}
        if "theme" in known:
            known["theme"] = THEME_KEYS.get(str(known["theme"]), "dark")
        if "accent" in known:
            known["accent"] = ACCENT_KEYS.get(str(known["accent"]), "green")
        return cls(**known)


def load_settings() -> Settings:
    if SETTINGS_PATH.exists():
        try:
            return Settings.from_json(json.loads(SETTINGS_PATH.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, TypeError):
            pass
    return Settings()


def save_settings(settings: Settings) -> None:
    SETTINGS_PATH.write_text(
        json.dumps(settings.to_json(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@dataclass
class Pet:
    name: str = "Комочек"
    species: SpeciesId = "zhar"
    temperament: Temperament = "snark"
    save_id: str = ""
    created_at: str = field(default_factory=now_iso)
    hunger: int = 55
    mood: int = 60
    health: int = 80
    age_ticks: int = 0
    stage: Stage = "яйцо"
    sick: bool = False
    alive: bool = True
    last_tick: str = field(default_factory=now_iso)
    journal: list[str] = field(default_factory=list)
    xp: int = 0
    level: int = 1
    coins: int = 5
    inventory: list[str] = field(default_factory=list)
    equipped: list[str] = field(default_factory=list)
    relics: list[str] = field(default_factory=list)
    floor_used: bool = False
    run_result: str = ""

    def species_info(self) -> dict:
        return SPECIES.get(self.species, SPECIES["zhar"])

    def type_name(self) -> str:
        return self.species_info()["type"]

    def mods(self) -> dict:
        m = dict(self.species_info()["mods"])
        for item_id in self.equipped:
            extra = SHOP.get(item_id, {}).get("mods") or {}
            for key, val in extra.items():
                if key in m:
                    m[key] = m[key] * val
        for rid in self.relics:
            extra = RELICS.get(rid, {}).get("mods") or {}
            for key, val in extra.items():
                if key in m:
                    m[key] = m[key] * val
        return m

    def click_value(self) -> int:
        extra = 1
        for rid in self.relics:
            extra = max(extra, int(RELICS.get(rid, {}).get("click", 1)))
        return extra

    def tap(self) -> int:
        if not self.alive:
            return 0
        gain = self.click_value()
        self.add_coins(gain)
        return gain

    def finish_run(self) -> dict:
        """Death or legend. Writes relics into meta. Returns loot card."""
        if self.run_result:
            return {"already": True}
        meta = load_meta()
        meta["runs"] = int(meta.get("runs", 0)) + 1
        meta["best_level"] = max(int(meta.get("best_level", 1)), self.level)
        shards = 2 + self.level
        if self.level >= 5:
            shards += 5
            self.run_result = "legend"
        else:
            self.run_result = "dead"
        meta["shards"] = int(meta.get("shards", 0)) + shards
        pool = ["warm_core", "quiet_bell", "fat_wallet", "second_chance"]
        if self.level >= 5:
            pool.append("legend_seed")
        if self.mood < 20:
            drop = "quiet_bell"
        elif self.hunger > 50:
            drop = "warm_core"
        elif self.coins >= 80:
            drop = "fat_wallet"
        else:
            drop = random.choice(pool)
        unlocked = list(meta.get("relics") or [])
        if drop not in unlocked:
            unlocked.append(drop)
        meta["relics"] = unlocked
        save_meta(meta)
        self.log(f"Забег закрыт. +{shards} осколков. Реликвия: {RELICS[drop]['name']}.")
        return {"shards": shards, "relic": drop, "result": self.run_result}

    def xp_needed(self) -> int:
        return LEVEL_XP.get(self.level, 9999)

    def xp_ratio(self) -> float:
        need = self.xp_needed()
        return 0 if need <= 0 else max(0.0, min(1.0, self.xp / need))

    def stage_label(self) -> str:
        return LEVEL_STAGE.get(self.level, self.stage)

    def add_xp(self, amount: int) -> str | None:
        if not self.alive or amount == 0:
            return None
        self.xp = max(0, self.xp + amount)
        msg = None
        guard = 0
        while self.level < 6 and self.xp >= self.xp_needed() and guard < 8:
            self.xp -= self.xp_needed()
            self.level += 1
            self.stage = LEVEL_STAGE.get(self.level, self.stage)
            msg = f"Уровень {self.level}: теперь {self.stage}."
            self.log(msg)
            if self.level >= 5 and not self.run_result:
                self.finish_run()
                msg = "Легенда. Забег выигран."
                self.log(msg)
            guard += 1
        return msg

    def add_coins(self, amount: int) -> None:
        self.coins = max(0, int(self.coins) + int(amount))

    def buy(self, item_id: str) -> str:
        item = SHOP.get(item_id)
        if not item:
            return "Такого нет в прилавке."
        if self.coins < item["price"]:
            return "Тута-коинов не хватает. Иди в аркаду."
        self.coins -= item["price"]
        self.inventory.append(item_id)
        self.log(f"Купил {item['icon']} {item['name']} за {item['price']}₮.")
        return f"В инвентаре: {item['name']}."

    def use_item(self, item_id: str, settings: Settings | None = None) -> str:
        if item_id not in self.inventory:
            return "Этого у тебя нет."
        item = SHOP[item_id]
        if item["kind"] == "cosmetic":
            if item_id in self.equipped:
                self.equipped.remove(item_id)
                self.log(f"Снял {item['name']}.")
                return f"Снято: {item['name']}."
            self.equipped.append(item_id)
            self.log(f"Надел {item['name']}.")
            return f"Надето: {item['name']}."
        self.inventory.remove(item_id)
        effect = item.get("effect") or {}
        if item.get("prefer") and item["prefer"] != self.species:
            self.mood -= 6
            self.hunger += int(effect.get("hunger", 0) * 0.4)
            self.log(f"{item['name']} ему не зашло.")
            self.clamp(settings)
            return "Не его вкус. Настроение упало."
        self.hunger += int(effect.get("hunger", 0))
        self.mood += int(effect.get("mood", 0))
        self.health += int(effect.get("health", 0))
        if effect.get("cure") and self.health >= 35:
            self.sick = False
        self.add_xp(int(effect.get("xp", 0)))
        self.clamp(settings)
        self.log(f"Использовал {item['name']}.")
        return f"{item['name']} пошло в дело."

    def clamp(self, settings: Settings | None = None) -> None:
        settings = settings or load_settings()
        self.hunger = max(0, min(100, int(self.hunger)))
        self.mood = max(0, min(100, int(self.mood)))
        floor = 1 if settings.immortal else 0
        self.health = max(floor, min(100, int(self.health)))
        if settings.immortal and self.health <= 1:
            self.alive = True

    def mood_name(self) -> MoodName:
        if self.mood >= 80:
            return "восторженный"
        if self.mood >= 50:
            return "нормальный"
        if self.mood >= 25:
            return "печальный"
        if self.mood >= 8:
            return "злой"
        return "мертв внутри"

    def log(self, text: str) -> None:
        self.journal.append(f"[{now_stamp()}] {text}")
        if len(self.journal) > 80:
            self.journal = self.journal[-80:]

    def _say(self, bucket: str) -> str:
        return random.choice(PASSIVE_AGGRO[bucket])

    def _tkey(self) -> str:
        return self.temperament if self.temperament in TEMPER_MODS else "snark"

    def _tmod(self) -> float:
        return TEMPER_MODS[self._tkey()]["mood_hits"]

    def feed(self, settings: Settings | None = None) -> str:
        if not self.alive:
            return "Он уже не ест. Это метафора."
        m = self.mods()
        self.hunger += int(22 * m["feed_hunger"])
        self.mood += int((4 if self.hunger < 90 else -6) * self._tmod())
        if self.hunger > 95:
            self.health -= int(4 * m["overfeed_dmg"])
            msg = "Перекормил. Теперь ему плохо и стыдно за тебя."
        else:
            msg = self._say("feed")
        self.add_xp(5)
        self.clamp(settings)
        self.log(f"Кормёжка. {msg}")
        return msg

    def play(self, settings: Settings | None = None) -> str:
        if not self.alive:
            return "Играть с отсутствием — отдельный жанр."
        m = self.mods()
        if self.hunger < 15:
            msg = "Он слишком голоден, чтобы притворяться весёлым."
            self.mood -= int(8 * self._tmod())
        else:
            self.mood += int(16 * m["play_mood"])
            self.hunger -= 8
            self.health += 2
            self.add_xp(8)
            msg = self._say("play")
        self.clamp(settings)
        self.log(f"Игра. {msg}")
        return msg

    def ignore(self, settings: Settings | None = None) -> str:
        if not self.alive:
            return "Игнорировать мёртвого проще. Ты уже тренировался."
        m = self.mods()
        self.mood -= int(14 * m["ignore_mood"] * self._tmod())
        self.hunger -= 6
        self.add_xp(-7)
        msg = self._say("ignore")
        self.clamp(settings)
        self.log(f"Игнор. {msg}")
        return msg

    def heal(self, settings: Settings | None = None) -> str:
        if not self.alive:
            return "Поздно для витаминок."
        m = self.mods()
        self.health += int(18 * m["heal"])
        if self.health >= 40:
            self.sick = False
        self.mood += 3
        self.add_xp(4)
        self.clamp(settings)
        msg = "Лекарство принято. Благодарность — опциональна."
        self.log(f"Лечение. {msg}")
        return msg

    def tick(self, settings: Settings | None = None) -> str | None:
        settings = settings or load_settings()
        if not self.alive:
            return None
        m = self.mods()
        self.age_ticks += 1
        if self.mood < 25:
            extra = 1 if random.random() < (m["spite_evo"] - 1) * 0.5 else 0
            self.age_ticks += extra
        self.hunger -= max(1, int(2 * m["hunger_decay"]))
        self.mood -= max(1, int(1 * m["mood_decay"] * self._tmod()))
        if self.hunger < 20 or self.mood < 15:
            self.health -= max(1, int(4 * m["health_decay"]))
        if self.health < 35 and random.random() < 0.25 * m["sick_chance"]:
            self.sick = True
        if self.sick:
            self.health -= max(1, int(3 * m["health_decay"]))
            self.mood -= 2
        if self.hunger < 20 or self.mood < 15:
            self.add_xp(-4)
        else:
            self.add_xp(2)
        self.clamp(settings)
        self.last_tick = now_iso()
        self._maybe_evolve()
        died = self.health <= 0 or (self.hunger <= 0 and self.mood <= 0)
        if died and not settings.immortal:
            if any(RELICS.get(r, {}).get("floor_once") for r in self.relics) and not self.floor_used:
                self.health = 15
                self.hunger = max(self.hunger, 12)
                self.floor_used = True
                self.alive = True
                msg = "Второй шанс сработал. Больше такого не будет."
                self.log(msg)
                return msg
            self.alive = False
            self.sick = False
            self.finish_run()
            msg = "Он погас. На экране. Ты смотрел."
            self.log(msg)
            return msg
        if died and settings.immortal:
            self.health = 1
            self.alive = True
            if random.random() < 0.3:
                msg = "Режим милосердия. Он жив из принципа, не из любви."
                self.log(msg)
                return msg
        talk_p = 0.22 * m["idle_talk"] * TEMPER_MODS[self._tkey()]["talk"]
        if self.sick and random.random() < 0.4:
            msg = self._say("sick")
            self.log(msg)
            return msg
        if random.random() < talk_p:
            msg = self._say("idle")
            self.log(msg)
            return msg
        return None

    def catch_up(self, settings: Settings | None = None) -> str | None:
        settings = settings or load_settings()
        if not self.alive:
            self.last_tick = now_iso()
            return None
        try:
            last = datetime.fromisoformat(self.last_tick)
        except ValueError:
            self.last_tick = now_iso()
            return None
        step = max(2, int(settings.tick_seconds))
        elapsed = (datetime.now() - last).total_seconds()
        steps = min(int(elapsed // step), 40)
        last_msg = None
        for _ in range(steps):
            last_msg = self.tick(settings) or last_msg
            if not self.alive:
                break
        if steps == 0:
            self.last_tick = now_iso()
        return last_msg

    def _maybe_evolve(self) -> None:
        mapped = LEVEL_STAGE.get(self.level)
        if mapped and mapped != self.stage:
            self.stage = mapped
            self.log(f"Эволюция → {self.stage}. Уровень {self.level}.")

    def lifetime_label(self) -> str:
        try:
            born = datetime.fromisoformat(self.created_at)
        except ValueError:
            return f"{self.age_ticks} тиков"
        sec = int((datetime.now() - born).total_seconds())
        if sec < 60:
            return f"{sec} с"
        if sec < 3600:
            return f"{sec // 60} мин"
        if sec < 86400:
            return f"{sec // 3600} ч {(sec % 3600) // 60} мин"
        return f"{sec // 86400} д {(sec % 86400) // 3600} ч"

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> "Pet":
        known = {k: data[k] for k in cls.__dataclass_fields__ if k in data}
        if known.get("species") not in SPECIES:
            known["species"] = "zhar"
        known.setdefault("xp", 0)
        known.setdefault("level", 1)
        known.setdefault("coins", 5)
        known.setdefault("inventory", [])
        known.setdefault("equipped", [])
        known.setdefault("relics", [])
        known.setdefault("floor_used", False)
        known.setdefault("run_result", "")
        return cls(**known)


def create_pet(
    name: str,
    species: SpeciesId,
    temperament: Temperament = "snark",
    start_care: StartCare = "normal",
    relic_id: str | None = None,
) -> Pet:
    stats = START_STATS.get(start_care, START_STATS["normal"])
    coins = 5
    xp = 0
    relics: list[str] = []
    if relic_id and relic_id in RELICS:
        relics = [relic_id]
        coins += int(RELICS[relic_id].get("start_coins", 0))
        xp += int(RELICS[relic_id].get("start_xp", 0))
    pet = Pet(
        name=name.strip() or SPECIES[species]["title"],
        species=species,
        temperament=temperament,
        save_id=slugify(name or species),
        hunger=stats["hunger"],
        mood=stats["mood"],
        health=stats["health"],
        coins=coins,
        xp=xp,
        level=1,
        stage="яйцо",
        relics=relics,
    )
    info = SPECIES[species]
    tlab = TEMPER_MODS.get(pet._tkey(), {}).get("label", pet.temperament)
    pet.log(f"Рождён {info['title']} ({info['type']}), характер: {tlab}.")
    return pet


def save_path(save_id: str) -> Path:
    return SAVES_DIR / f"{save_id}.json"


def save_pet(pet: Pet) -> None:
    if not pet.save_id:
        pet.save_id = slugify(pet.name)
    save_path(pet.save_id).write_text(
        json.dumps(pet.to_json(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_pet(save_id: str) -> Pet | None:
    path = save_path(save_id)
    if not path.exists():
        return None
    try:
        return Pet.from_json(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, TypeError, KeyError):
        return None


def list_saves() -> list[Pet]:
    _migrate_old_save()
    pets: list[Pet] = []
    for path in sorted(SAVES_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            pets.append(Pet.from_json(json.loads(path.read_text(encoding="utf-8"))))
        except (json.JSONDecodeError, TypeError, KeyError):
            continue
    return pets


def delete_save(save_id: str) -> None:
    path = save_path(save_id)
    if path.exists():
        path.unlink()


def _migrate_old_save() -> None:
    if not OLD_SAVE.exists():
        return
    try:
        data = json.loads(OLD_SAVE.read_text(encoding="utf-8"))
        pet = Pet.from_json(data)
        if not pet.save_id:
            pet.save_id = slugify(pet.name)
        if not save_path(pet.save_id).exists():
            save_pet(pet)
        OLD_SAVE.unlink()
    except (json.JSONDecodeError, TypeError, OSError):
        pass
