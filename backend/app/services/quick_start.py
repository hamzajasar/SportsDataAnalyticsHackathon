"""Quick start: turn a few answers a club volunteer actually knows into a full club profile.

Everything not given is estimated, and every estimate is reported back (`estimated` + `notes`), so
the app can say "we assumed X — change it if you know better".
"""

import math
import unicodedata
from functools import lru_cache

import pandas as pd

from app.i18n import Lang, count, num, t
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


def quick_club(a: dict, lang: Lang = "en") -> dict:
    estimated: list[str] = []
    notes: list[str] = []

    # Location
    if a.get("lat") is not None and a.get("lon") is not None:
        lat, lon = a["lat"], a["lon"]
    else:
        city = find_city(a["city"])
        if city is None:
            raise KeyError(t("quick.unknown_city", lang, city=a["city"]))
        lat, lon = city["lat"], city["lon"]
        estimated.append("location")
        notes.append(t("quick.location", lang, city=city["city"]))

    # Electricity per year
    price = actions.cost_assumptions()["electricity_price"]
    heating_type = a.get("heating_type") or "unknown"
    if a.get("yearly_kwh"):
        kwh = a["yearly_kwh"]
    elif a.get("monthly_bill_km"):
        kwh = a["monthly_bill_km"] * 12 / price
        estimated.append("electricity_kwh_year")
        notes.append(
            t(
                "quick.bill",
                lang,
                bill=num(a["monthly_bill_km"], lang),
                price=num(price, lang, 3),
                kwh=num(kwh, lang),
            )
        )
    else:
        kwh = a["teams"] * KWH_PER_TEAM_YEAR
        estimated.append("electricity_kwh_year")
        notes.append(
            t("quick.no_bill", lang, per_team=num(KWH_PER_TEAM_YEAR, lang), kwh=num(kwh, lang))
        )

    split = SPLIT_ELECTRIC_HEATING if heating_type == "electric" else SPLIT_OTHER_HEATING
    estimated.append("electricity_split")
    notes.append(t("quick.split" if heating_type == "electric" else "quick.split_no_heating", lang))
    if heating_type == "unknown":
        notes.append(t("quick.heating_unknown", lang))

    # Away travel
    away = a.get("away_games_per_team")
    if away is None:
        away = DEFAULT_AWAY_GAMES
        estimated.append("away_trips_per_team_year")
        notes.append(t("quick.away_games", lang, n=DEFAULT_AWAY_GAMES))
    km = a.get("avg_one_way_km")
    if km is None:
        km = DEFAULT_ONE_WAY_KM
        estimated.append("avg_one_way_km")
        notes.append(t("quick.distance", lang, km=DEFAULT_ONE_WAY_KM))
    transport = a.get("transport") or "mixed"
    vehicles = _vehicles(transport)
    estimated.append("vehicles_per_trip")
    notes.append(
        t(
            "quick.vehicles",
            lang,
            people=PEOPLE_PER_TRIP,
            transport=t(f"transport.{transport}", lang),
            minibuses=count(vehicles["minibus"], "minibus", lang),
            cars=count(vehicles["car"], "car", lang),
        )
    )

    club = {
        "name": a.get("name") or t("quick.default_name", lang),
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
        notes.append(t("quick.not_paying", lang))
    return {"club": club, "estimated": estimated, "notes": notes}
