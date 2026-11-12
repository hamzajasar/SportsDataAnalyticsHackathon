"""Quick start: turn a few answers a club volunteer actually knows into a full club profile.

Everything not given is estimated, and every estimate is reported back (`estimated` + `notes`), so
the app can say "we assumed X — change it if you know better".
"""

import math
import unicodedata
from functools import lru_cache

import pandas as pd

from app.services import actions
from app.services.emissions import REFERENCE_DIR

# Typical split of a club's electricity, from the reference club (22k floodlights, 20k electric
# heating, 10k hall of 52k kWh). Without electric heating: floodlights and hall in the same ratio.
SPLIT_ELECTRIC_HEATING = {"floodlights": 0.42, "heating": 0.38, "hall_and_other": 0.20}
SPLIT_OTHER_HEATING = {"floodlights": 0.69, "heating": 0.0, "hall_and_other": 0.31}
KWH_PER_TEAM_YEAR = 52000 / 6  # reference club: 52,000 kWh for 6 teams (rough estimate)
DEFAULT_AWAY_GAMES = 12  # per team per season (assumption)
DEFAULT_ONE_WAY_KM = 45  # reference club
PEOPLE_PER_TRIP = 18  # squad + staff (assumption)
SEATS = {"car": 3, "minibus": 8}  # people per vehicle (assumption)


def _fold(s: str) -> str:
    """'Bihać' -> 'bihac', so 'bihac' or 'BIHAĆ' still match. Handles đ (no decomposition)."""
    s = s.strip().lower().replace("đ", "dj")
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


@lru_cache
def cities() -> list[dict]:
    df = pd.read_csv(REFERENCE_DIR / "bih_cities.csv")
    return df.to_dict("records")


def find_city(name: str) -> dict | None:
    key = _fold(name)
    return next((c for c in cities() if _fold(c["city"]) == key), None)


def _vehicles(transport: str) -> dict:
    p = PEOPLE_PER_TRIP
    if transport == "cars":
        return {"minibus": 0, "car": math.ceil(p / SEATS["car"])}
    if transport == "minibus":
        return {
            "minibus": p // SEATS["minibus"],
            "car": math.ceil((p % SEATS["minibus"]) / SEATS["car"]),
        }
    # mixed: one minibus, the rest by car
    return {"minibus": 1, "car": math.ceil((p - SEATS["minibus"]) / SEATS["car"])}


def quick_club(a: dict) -> dict:
    estimated: list[str] = []
    notes: list[str] = []

    # Location
    if a.get("lat") is not None and a.get("lon") is not None:
        lat, lon = a["lat"], a["lon"]
    else:
        city = find_city(a["city"])
        if city is None:
            raise KeyError(f"Unknown city: {a['city']}. Pick one from /api/cities or send lat/lon.")
        lat, lon = city["lat"], city["lon"]
        estimated.append("location")
        notes.append(f"Location: centre of {city['city']} (used to find nearby pitches and clubs).")

    # Electricity per year
    price = actions.cost_assumptions()["electricity_price"]
    heating_type = a.get("heating_type") or "unknown"
    if a.get("yearly_kwh"):
        kwh = a["yearly_kwh"]
    elif a.get("monthly_bill_km"):
        kwh = a["monthly_bill_km"] * 12 / price
        estimated.append("electricity_kwh_year")
        notes.append(
            f"Electricity: {a['monthly_bill_km']:.0f} KM a month ÷ {price} KM/kWh "
            f"≈ {kwh:,.0f} kWh a year."
        )
    else:
        kwh = a["teams"] * KWH_PER_TEAM_YEAR
        estimated.append("electricity_kwh_year")
        notes.append(
            f"Electricity: no bill given, so a rough estimate of {KWH_PER_TEAM_YEAR:,.0f} kWh "
            f"per team ({kwh:,.0f} kWh a year). Enter your bill for a real number."
        )

    split = SPLIT_ELECTRIC_HEATING if heating_type == "electric" else SPLIT_OTHER_HEATING
    estimated.append("electricity_split")
    notes.append(
        "Split of electricity (floodlights / heating / hall) is typical, not measured"
        + ("." if heating_type == "electric" else "; heating is not electric so it isn't counted.")
    )
    if heating_type == "unknown":
        notes.append("Heating type unknown: we assume it isn't electric. Change it if it is.")

    # Away travel
    away = a.get("away_games_per_team")
    if away is None:
        away = DEFAULT_AWAY_GAMES
        estimated.append("away_trips_per_team_year")
        notes.append(f"Away games: assumed {DEFAULT_AWAY_GAMES} per team per season.")
    km = a.get("avg_one_way_km")
    if km is None:
        km = DEFAULT_ONE_WAY_KM
        estimated.append("avg_one_way_km")
        notes.append(f"Distance to away games: assumed {DEFAULT_ONE_WAY_KM} km one way.")
    transport = a.get("transport") or "mixed"
    vehicles = _vehicles(transport)
    estimated.append("vehicles_per_trip")
    notes.append(
        f"Vehicles per trip for {PEOPLE_PER_TRIP} people ({transport}): "
        f"{vehicles['minibus']} minibus(es), {vehicles['car']} car(s)."
    )

    club = {
        "name": a.get("name") or "My club",
        "city": a["city"],
        "lat": lat,
        "lon": lon,
        "children": a["children"],
        "teams": a["teams"],
        "electricity_kwh_year": {k: round(kwh * v) for k, v in split.items()},
        "travel": {
            "away_trips_per_team_year": away,
            "avg_one_way_km": km,
            "vehicles_per_trip": vehicles,
        },
        "pays_electricity": a.get("pays_electricity", True),
        "heating_type": heating_type,
    }
    if not club["pays_electricity"]:
        notes.append(
            "The club doesn't pay electricity: facility upgrades will be shown as proposals "
            "for the facility owner."
        )
    return {"club": club, "estimated": estimated, "notes": notes}
