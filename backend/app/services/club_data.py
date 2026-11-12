"""Club-level data, assumptions, venues and sources.

One source per number:
- app/reference/*.csv (committed, built by `make reference`):
    emission_factors, grid_intensity, electricity_mix   -> services/emissions.py
    sport_venues_bih, pv_yield_sarajevo, sarajevo_temperature, cost_assumptions -> this module
- data/clean/*.json (committed): only what has no reference table yet —
    sample_club.json, upgrades.json, sources.json
data/clean/grid_factor.json and vehicle_factors.json duplicate the reference tables and are not
read by the API.
"""

import json
import math
from functools import lru_cache
from typing import Any

import pandas as pd

from app.core.config import settings
from app.services.emissions import REFERENCE_DIR

# Only these files can be served — never build a path from user input.
JSON_FILES = {
    "sample_club": "sample_club.json",
    "upgrades": "upgrades.json",
    "sources": "sources.json",
}
CSV_FILES = {
    "venues": "sport_venues_bih.csv",
    "pv_yield": "pv_yield_sarajevo.csv",
    "temperature": "sarajevo_temperature.csv",
    "costs": "cost_assumptions.csv",
}


@lru_cache
def load_json(name: str) -> Any:
    if name not in JSON_FILES:
        raise KeyError(name)
    path = settings.data_dir / "clean" / JSON_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"data/clean/{JSON_FILES[name]} is missing — run git pull")
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache
def load_csv(name: str) -> pd.DataFrame:
    if name not in CSV_FILES:
        raise KeyError(name)
    path = REFERENCE_DIR / CSV_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"backend/app/reference/{CSV_FILES[name]} is missing — git pull")
    return pd.read_csv(path)


def _records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records"))  # NaN -> null


def _monthly(name: str, col: str) -> list[dict]:
    df = load_csv(name)
    return [
        {"month": int(m), "value": float(v), "source": src}
        for m, v, src in zip(df["month"], df[col], df["source"], strict=True)
    ]


def sample_club() -> dict:
    return load_json("sample_club")


def assumptions() -> dict:
    return {
        "costs": _records(load_csv("costs")),
        "upgrades": load_json("upgrades"),
        "pv_yield_monthly": _monthly("pv_yield", "kwh_per_kwp"),
        "temperature_monthly": _monthly("temperature", "mean_temp_c"),
    }


def sources() -> list[dict]:
    return load_json("sources")["sources"]


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
    df = load_csv("venues").dropna(subset=["lat", "lon"])
    if leisure:
        df = df[df["leisure"] == leisure]
    out = []
    for v in _records(df):
        item = {
            "id": v["osm_id"],
            "name": v["name"] or None,
            "leisure": v["leisure"],
            "sport": v["sport"] or None,
            "lat": v["lat"],
            "lon": v["lon"],
            "distance_km": None,
        }
        if near is not None:
            d = _haversine_km(near[0], near[1], v["lat"], v["lon"])
            if radius_km is not None and d > radius_km:
                continue
            item["distance_km"] = round(d, 2)
        out.append(item)
    if near is not None:
        out.sort(key=lambda v: v["distance_km"])
    return out[:limit]
