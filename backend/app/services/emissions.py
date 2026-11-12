"""Carbon calculations for a community sports club (Topic 6).

All numbers come from the committed reference tables in app/reference/ (built by `make reference`):
- grid_intensity.csv    gCO2 per kWh of electricity, per country & year (Ember)
- electricity_mix.csv   share of electricity by source (Ember)
- emission_factors.csv  kg CO2e per km / passenger-km / kWh / litre / kg (UK Gov GHG factors 2025)

Keep every function pure and explainable: return the factor used and its source, so the UI can
show *how* a number was calculated (judging: analytical soundness).
"""

import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.i18n import Lang, count, num, t

REFERENCE_DIR = Path(__file__).resolve().parents[1] / "reference"

# Aliases so the API accepts friendly names
ENTITY_ALIASES = {"EU": "European Union (27)", "EU27": "European Union (27)"}


@lru_cache
def grid_table() -> pd.DataFrame:
    return pd.read_csv(REFERENCE_DIR / "grid_intensity.csv")


@lru_cache
def mix_table() -> pd.DataFrame:
    return pd.read_csv(REFERENCE_DIR / "electricity_mix.csv")


@lru_cache
def factor_table() -> pd.DataFrame:
    return pd.read_csv(REFERENCE_DIR / "emission_factors.csv")


def _country_rows(df: pd.DataFrame, country: str) -> pd.DataFrame:
    """Match by ISO3 code (BIH), entity name (Croatia) or alias (EU)."""
    name = ENTITY_ALIASES.get(country.upper(), country)
    rows = df[
        (df["code"].str.upper() == country.upper()) | (df["entity"].str.lower() == name.lower())
    ]
    if rows.empty:
        raise KeyError(f"Unknown country/region: {country}")
    return rows


@dataclass(frozen=True)
class GridIntensity:
    entity: str
    code: str | None
    year: int
    gco2_per_kwh: float
    source: str


def grid_intensity(country: str, year: int | None = None) -> GridIntensity:
    """Intensity for `year`, or the latest year available at or before it."""
    rows = _country_rows(grid_table(), country)
    if year is not None:
        rows = rows[rows["year"] <= year]
        if rows.empty:
            raise KeyError(f"No grid intensity for {country} at or before {year}")
    r = rows.sort_values("year").iloc[-1]
    return GridIntensity(
        entity=r["entity"],
        code=None if pd.isna(r["code"]) else r["code"],
        year=int(r["year"]),
        gco2_per_kwh=float(r["gco2_per_kwh"]),
        source=r["source"],
    )


def grid_series(countries: list[str], from_year: int = 2000) -> list[dict]:
    out = []
    for c in countries:
        rows = _country_rows(grid_table(), c)
        rows = rows[rows["year"] >= from_year].sort_values("year")
        out.append(
            {
                "entity": rows["entity"].iloc[0],
                "code": c.upper(),
                "points": [
                    {"year": int(y), "gco2_per_kwh": float(v)}
                    for y, v in zip(rows["year"], rows["gco2_per_kwh"], strict=True)
                ],
            }
        )
    return out


def electricity_mix(country: str, year: int | None = None) -> dict:
    rows = _country_rows(mix_table(), country)
    if year is not None:
        rows = rows[rows["year"] <= year]
    r = rows.sort_values("year").iloc[-1]
    shares = {
        c.removesuffix("_pct"): float(r[c])
        for c in rows.columns
        if c.endswith("_pct") and not pd.isna(r[c])
    }
    return {
        "entity": r["entity"],
        "year": int(r["year"]),
        "shares_pct": shares,
        "source": r["source"],
    }


def electricity_emissions(kwh: float, country: str = "BIH", year: int | None = None) -> dict:
    gi = grid_intensity(country, year)
    return {
        "kwh": kwh,
        "kg_co2e": round(kwh * gi.gco2_per_kwh / 1000, 2),
        "country": gi.entity,
        "year": gi.year,
        "gco2_per_kwh": gi.gco2_per_kwh,
        "source": gi.source,
    }


def factor(key: str) -> dict:
    rows = factor_table()
    hit = rows[rows["key"] == key]
    if hit.empty:
        raise KeyError(f"Unknown emission factor: {key}")
    r = hit.iloc[0]
    return {"key": key, "unit": r["unit"], "kg_co2e": float(r["kg_co2e"]), "source": r["source"]}


def amount_emissions(key: str, amount: float) -> dict:
    """Fuel/waste/etc.: amount in the factor's unit (kWh, litre, kg…) -> kg CO2e."""
    f = factor(key)
    return {**f, "amount": amount, "total_kg_co2e": round(amount * f["kg_co2e"], 2)}


# ---- Travel ---------------------------------------------------------------------------------

VAN_SEATS = 8  # minibus/van for a youth team (assumption, shown in UI)
COACH_SEATS = 50  # one hired coach per 50 people
# UK factors give coach emissions per PASSENGER-km at average UK occupancy. A hired coach emits the
# same whether it carries 18 or 50 people, so we convert to a per-VEHICLE-km factor:
# per-passenger-km factor x assumed average occupancy (assumption, shown in UI).
COACH_AVG_OCCUPANCY = 35
CAR_KEYS = {"car_average", "car_small", "car_large", "car_diesel", "car_petrol", "car_hybrid"}


def trip_options(
    distance_km: float,
    people: int,
    round_trip: bool = True,
    car_occupancy: int = 3,
    car_type: str = "car_average",
    lang: Lang = "en",
) -> dict:
    """Compare ways to get a squad to an away game. Returns options sorted by kg CO2e."""
    if car_type not in CAR_KEYS:
        raise KeyError(f"Unknown car type: {car_type}")
    km = distance_km * (2 if round_trip else 1)
    opts = []

    cars = math.ceil(people / car_occupancy)
    f = factor(car_type)
    opts.append(
        {
            "mode": "cars",
            "label": t("travel.cars", lang, cars=count(cars, "car", lang), occ=car_occupancy),
            "vehicles": cars,
            "kg_co2e": round(cars * km * f["kg_co2e"], 1),
            "assumption": t("trip.per_car_km", lang, f=num(f["kg_co2e"], lang, 3)),
        }
    )

    vans = math.ceil(people / VAN_SEATS)
    f = factor("van_average")
    opts.append(
        {
            "mode": "minibus",
            "label": t(
                "travel.minibuses", lang, minibuses=count(vans, "minibus", lang), seats=VAN_SEATS
            ),
            "vehicles": vans,
            "kg_co2e": round(vans * km * f["kg_co2e"], 1),
            "assumption": t("trip.per_van_km", lang, f=num(f["kg_co2e"], lang, 3)),
        }
    )

    # Hired coach: emissions per vehicle, not per passenger (an emptier coach emits the same).
    coaches = math.ceil(people / COACH_SEATS)
    per_vehicle_km = factor("coach")["kg_co2e"] * COACH_AVG_OCCUPANCY
    opts.append(
        {
            "mode": "coach",
            "label": t(
                "travel.coach", lang, coaches=count(coaches, "coach", lang), seats=COACH_SEATS
            ),
            "vehicles": coaches,
            "kg_co2e": round(coaches * km * per_vehicle_km, 1),
            "assumption": t(
                "trip.per_coach_km",
                lang,
                f=num(per_vehicle_km, lang, 3),
                pkm=num(factor("coach")["kg_co2e"], lang, 5),
                occ=COACH_AVG_OCCUPANCY,
            ),
        }
    )

    # Train: a scheduled service runs anyway, so the per-passenger factor is the right basis.
    f = factor("rail")
    opts.append(
        {
            "mode": "rail",
            "label": t("trip.rail", lang),
            "vehicles": None,
            "kg_co2e": round(people * km * f["kg_co2e"], 1),
            "assumption": t("trip.per_pkm", lang, f=num(f["kg_co2e"], lang, 3)),
        }
    )

    opts.sort(key=lambda o: o["kg_co2e"])
    worst = max(o["kg_co2e"] for o in opts)
    for o in opts:
        o["saving_vs_worst_kg"] = round(worst - o["kg_co2e"], 1)
    return {
        "distance_km": distance_km,
        "total_km": km,
        "people": people,
        "options": opts,
        "source": factor("coach")["source"],
    }
