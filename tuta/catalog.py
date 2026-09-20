from __future__ import annotations

from typing import Any

from tuta.pet import RELICS, SPECIES, TEMPER_MODS

SPECIES_SHORT = {"zhar": "Zh", "sashochek": "Tp", "morok": "Mo"}
TEMPER_SHORT = {"soft": "So", "snark": "Sn", "venom": "Ve"}


def catalog() -> dict[str, Any]:
    species = {}
    for sid, spec in SPECIES.items():
        species[sid] = {
            "title": spec["title"],
            "type": spec["type"],
            "blurb": spec["blurb"],
            "palette": spec["palette"],
            "frames": spec["frames"],
            "short": SPECIES_SHORT.get(sid, sid[:2].title()),
        }
    return {
        "species": species,
        "tempers": {k: v["label"] for k, v in TEMPER_MODS.items()},
        "temper_short": TEMPER_SHORT,
        "relics": RELICS,
    }


def char_code(species: str, temper: str) -> str:
    return SPECIES_SHORT.get(species, "??") + TEMPER_SHORT.get(temper, "??")
