"""Turn data/clean/*.json into small CSV reference tables in backend/app/reference/.
Run after fetch_data.py: python scripts/build_reference.py
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN, REF = ROOT / "data" / "clean", ROOT / "backend" / "app" / "reference"


def load(n):
    return json.loads((CLEAN / n).read_text(encoding="utf-8"))


def write(name, header, rows):
    with open(REF / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")  # LF, so rebuilds don't create fake diffs
        w.writerow(header)
        w.writerows(rows)
    print("wrote", name, len(rows), "rows")


mt = load("sarajevo_monthly_temp.json")
write(
    "sarajevo_temperature.csv",
    ["month", "mean_temp_c", "source"],
    [
        [m, t, "Open-Meteo historical weather, Sarajevo 2024-2025 (CC BY 4.0)"]
        for m, t in mt["monthly_mean_c"].items()
    ],
)

pv = load("pv_yield.json")
write(
    "pv_yield_sarajevo.csv",
    ["month", "kwh_per_kwp", "source"],
    [
        [m, v, "PVGIS (c) European Communities; tilt 35, south, 14% losses"]
        for m, v in pv["monthly_kwh_per_kwp"].items()
    ],
)

venues = load("osm_sport_venues.json")["venues"]
write(
    "sport_venues_bih.csv",
    ["osm_id", "name", "leisure", "sport", "lat", "lon", "source"],
    [
        [
            v["id"],
            v["name"] or "",
            v["leisure"],
            v["sport"] or "",
            v["lat"],
            v["lon"],
            "OpenStreetMap contributors (ODbL)",
        ]
        for v in venues
    ],
)

p, vf, club = load("prices.json"), load("vehicle_factors.json")["factors"], load("sample_club.json")
A = "ASSUMPTION - verify before use"
write(
    "cost_assumptions.csv",
    ["key", "value", "unit", "note", "source"],
    [
        [
            "electricity_price",
            p["electricity_km_per_kwh"],
            "KM/kWh",
            "non-household tariff estimate",
            A,
        ],
        [
            "fuel_cost_car",
            p["fuel_km_per_km_driven"]["car"],
            "KM/vehicle-km",
            "fuel cost per km driven",
            A,
        ],
        [
            "fuel_cost_minibus",
            p["fuel_km_per_km_driven"]["minibus"],
            "KM/vehicle-km",
            "fuel cost per km driven",
            A,
        ],
        [
            "minibus_kg_per_km",
            vf["minibus"]["value"],
            "kg CO2e/vehicle-km",
            vf["minibus"]["basis"],
            "UK GHG 2025 (OGL v3.0)",
        ],
        [
            "coach_kg_per_km",
            vf["coach"]["value"],
            "kg CO2e/vehicle-km",
            vf["coach"]["basis"],
            "UK GHG 2025 (OGL v3.0) + assumed occupancy",
        ],
    ],
)
