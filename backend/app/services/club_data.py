"""Club-level data and assumptions from data/clean/ (shared via git; see README "Where data goes").

Single source of truth per number:
- emission factors + grid intensity -> app/reference/*.csv  (services/emissions.py)
- club, prices, upgrades, solar yield, venues, sources -> data/clean/*.json (this module)

data/clean/grid_factor.json and vehicle_factors.json duplicate the reference tables and are NOT used
by the API (kept only so the original fetch script's output stays intact).
"""

import json
import math
from functools import lru_cache
from typing import Any

from app.core.config import settings

# Only these files can be served — never build a path from user input.
FILES = {
    "sample_club": "sample_club.json",
    "prices": "prices.json",
    "upgrades": "upgrades.json",
    "pv_yield": "pv_yield.json",
    "monthly_temp": "sarajevo_monthly_temp.json",
    "venues": "osm_sport_venues.json",
    "sources": "sources.json",
}


def clean_dir():
    return settings.data_dir / "clean"


@lru_cache
def load(name: str) -> Any:
    if name not in FILES:
        raise KeyError(name)
    path = clean_dir() / FILES[name]
    if not path.exists():
        raise FileNotFoundError(
            f"data/clean/{FILES[name]} is missing — git pull, or run the fetch script"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def sample_club() -> dict:
    return load("sample_club")


def assumptions() -> dict:
    return {
        "prices": load("prices"),
        "upgrades": load("upgrades"),
        "pv_yield": load("pv_yield"),
        "monthly_temp": load("monthly_temp"),
    }


def sources() -> list[dict]:
    return load("sources")["sources"]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def venues(
    leisure: str | None = None,
    near: tuple[float, float] | None = None,
    radius_km: float | None = None,
    limit: int = 5000,
) -> list[dict]:
    """OSM sports venues in BiH. Optional filter by type and by distance from a point."""
    out = []
    for v in load("venues")["venues"]:
        if v.get("lat") is None or v.get("lon") is None:
            continue
        if leisure and v.get("leisure") != leisure:
            continue
        item = {**v, "distance_km": None}
        if near is not None:
            d = _haversine_km(near[0], near[1], v["lat"], v["lon"])
            if radius_km is not None and d > radius_km:
                continue
            item["distance_km"] = round(d, 2)
        out.append(item)
    if near is not None:
        out.sort(key=lambda v: v["distance_km"])
    return out[:limit]
