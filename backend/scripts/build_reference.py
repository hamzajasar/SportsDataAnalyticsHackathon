"""Build the small, committed reference tables the app computes with (backend/app/reference/).

Usage: make reference   (needs `make data` first)

Raw downloads stay git-ignored; these derived slices are committed so the API, tests, CI and a
deployed server work without the raw files. Licences allow redistribution with attribution
(see docs/DATA_SOURCES.md) — the `source` column carries the credit.
"""

import pandas as pd

from app.core.config import settings
from app.services.emissions import REFERENCE_DIR

RAW = settings.data_dir / "raw" / "sustainability"
GHG_SOURCE = "UK Government GHG Conversion Factors 2025 (OGL v3.0)"
EMBER_SOURCE = "Ember via Our World in Data (CC BY 4.0)"

MIX_ENTITIES = [
    "Bosnia and Herzegovina", "Croatia", "Serbia", "Montenegro", "North Macedonia", "Albania",
    "Kosovo", "Slovenia", "Hungary", "Austria", "Italy", "Germany", "France", "Poland",
    "Greece", "Bulgaria", "Romania", "European Union (27)", "World",
]  # fmt: skip

# (category, key, ghg Level 1, Level 2, Level 3, Column Text, UOM, unit label)
FACTORS = [
    ("travel", "car_average", "Passenger vehicles", "Cars (by size)", "Average car", "Unknown", "km", "vehicle_km"),
    ("travel", "car_small", "Passenger vehicles", "Cars (by size)", "Small car", "Unknown", "km", "vehicle_km"),
    ("travel", "car_large", "Passenger vehicles", "Cars (by size)", "Large car", "Unknown", "km", "vehicle_km"),
    ("travel", "car_diesel", "Passenger vehicles", "Cars (by size)", "Average car", "Diesel", "km", "vehicle_km"),
    ("travel", "car_petrol", "Passenger vehicles", "Cars (by size)", "Average car", "Petrol", "km", "vehicle_km"),
    ("travel", "car_hybrid", "Passenger vehicles", "Cars (by size)", "Average car", "Hybrid", "km", "vehicle_km"),
    ("travel", "van_average", "Passenger vehicles", None, None, None, "km", "vehicle_km"),
    ("travel", "coach", "Business travel- land", "Bus", "Coach", None, "passenger.km", "passenger_km"),
    ("travel", "local_bus", "Business travel- land", "Bus", "Average local bus", None, "passenger.km", "passenger_km"),
    ("travel", "rail", "Business travel- land", "Rail", "National rail", None, "passenger.km", "passenger_km"),
    ("travel", "taxi", "Business travel- land", "Taxis", "Regular taxi", None, "passenger.km", "passenger_km"),
    ("energy", "natural_gas_kwh", "Fuels", "Gaseous fuels", "Natural gas", None, "kWh (Gross CV)", "kWh"),
    ("energy", "heating_oil_litre", "Fuels", "Liquid fuels", "Gas oil", None, "litres", "litre"),
    ("energy", "diesel_litre", "Fuels", "Liquid fuels", "Diesel (average biofuel blend)", None, "litres", "litre"),
    ("energy", "petrol_litre", "Fuels", "Liquid fuels", "Petrol (average biofuel blend)", None, "litres", "litre"),
    ("energy", "lpg_litre", "Fuels", None, "LPG", None, "litres", "litre"),
    ("energy", "coal_domestic_kg", "Fuels", "Solid fuels", "Coal (domestic)", None, "tonnes", "kg"),
    ("energy", "wood_logs_kg", "Bioenergy", "Biomass", "Wood logs", None, "tonnes", "kg"),
    ("energy", "wood_pellets_kg", "Bioenergy", "Biomass", "Wood pellets", None, "tonnes", "kg"),
]  # fmt: skip

WASTE_MATERIALS = [
    "Plastics: average plastics", "Clothing", "Paper and board: mixed", "Metal: mixed cans",
    "Glass", "Organic: food and drink waste", "Commercial and industrial waste",
    "WEEE - small", "Tyres", "Wood",
]  # fmt: skip
WASTE_ROUTES = {"Landfill": "landfill", "Open-loop": "recycling", "Closed-loop": "recycling_closed",
                "Combustion": "incineration", "Composting": "composting"}  # fmt: skip


def ghg_table() -> pd.DataFrame:
    df = pd.read_excel(
        RAW / "ghg_conversion_factors_2025_flat.xlsx", sheet_name="Factors by Category", header=5
    )
    return df[df["GHG/Unit"] == "kg CO2e"]


def pick(df, l1, l2, l3, col, uom) -> float:
    m = (df["Level 1"] == l1) & (df["UOM"] == uom)
    if l2 is not None:
        m &= df["Level 2"] == l2
    if l3 is not None:
        m &= df["Level 3"] == l3
    if col is not None:
        m &= df["Column Text"] == col
    hits = df[m]
    if l1 == "Passenger vehicles" and l2 is None and l3 is None:  # vans: average van, unknown fuel
        hits = df[(df["Level 1"] == "Delivery vehicles") & (df["Level 2"] == "Vans")
                  & (df["Level 3"] == "Average (up to 3.5 tonnes)") & (df["Column Text"] == "Unknown")
                  & (df["UOM"] == "km")]  # fmt: skip
    vals = hits["GHG Conversion Factor 2025"].dropna()
    if vals.empty:
        raise KeyError(f"No GHG factor for {l1} / {l2} / {l3} / {col} / {uom}")
    return float(vals.iloc[0])


def build_factors() -> pd.DataFrame:
    df = ghg_table()
    rows = []
    for cat, key, l1, l2, l3, col, uom, unit in FACTORS:
        v = pick(df, l1, l2, l3, col, uom)
        if uom == "tonnes":  # store per kg — friendlier for clubs
            v /= 1000
        rows.append({"category": cat, "key": key, "unit": unit, "kg_co2e": round(v, 6),
                     "source": GHG_SOURCE})  # fmt: skip
    waste = df[(df["Level 1"] == "Waste disposal") & (df["UOM"] == "tonnes")]
    for mat in WASTE_MATERIALS:
        for col, route in WASTE_ROUTES.items():
            hit = waste[
                (waste["Level 3"] == mat) & (waste["Column Text"].astype(str).str.startswith(col))
            ]
            v = hit["GHG Conversion Factor 2025"].dropna()
            if not v.empty:
                key = f"waste_{mat.split(':')[0].split(' -')[0].strip().lower().replace(' ', '_')}_{route}"
                rows.append({"category": "waste", "key": key, "unit": "kg",
                             "kg_co2e": round(float(v.iloc[0]) / 1000, 6), "source": GHG_SOURCE})  # fmt: skip
    # Production ("material use") factors: footprint of BUYING the item, new vs re-used/recycled.
    # This is where equipment's real footprint is — disposal factors above only count end of life.
    mat = df[(df["Level 1"] == "Material use") & (df["UOM"] == "tonnes")]
    routes = {
        "Primary material production": "new",
        "Re-used": "reused",
        "Closed-loop source": "recycled",
    }
    for name in ["Clothing", "Plastics: average plastics", "Tyres", "Metal: scrap metal",
                 "Paper and board: mixed", "Glass", "Wood"]:  # fmt: skip
        for col, route in routes.items():
            v = mat[(mat["Level 3"] == name) & (mat["Column Text"] == col)][
                "GHG Conversion Factor 2025"
            ]
            v = v.dropna()
            if not v.empty:
                slug = name.split(":")[0].strip().lower().replace(" ", "_")
                rows.append({"category": "material", "key": f"material_{slug}_{route}", "unit": "kg",
                             "kg_co2e": round(float(v.iloc[0]) / 1000, 6), "source": GHG_SOURCE})  # fmt: skip
    return pd.DataFrame(rows).drop_duplicates("key")


def main() -> None:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    ci = pd.read_csv(RAW / "carbon_intensity_electricity.csv")
    ci = ci.rename(columns={"co2_intensity__gco2_kwh": "gco2_per_kwh"})
    ci = ci[["entity", "code", "year", "gco2_per_kwh"]].dropna(subset=["gco2_per_kwh"])
    ci["source"] = EMBER_SOURCE
    ci.to_csv(REFERENCE_DIR / "grid_intensity.csv", index=False)

    mix = pd.read_csv(RAW / "electricity_mix_by_source.csv")
    mix = mix[mix.entity.isin(MIX_ENTITIES)]
    mix.columns = [c.replace("_share_of_electricity__pct", "_pct") for c in mix.columns]
    mix = mix.round(2)
    mix["source"] = EMBER_SOURCE
    mix.to_csv(REFERENCE_DIR / "electricity_mix.csv", index=False)

    f = build_factors()
    f.to_csv(REFERENCE_DIR / "emission_factors.csv", index=False)

    for p in sorted(REFERENCE_DIR.glob("*.csv")):
        print(f"  {p.name:<24} {len(pd.read_csv(p)):>6} rows  {p.stat().st_size / 1024:6.0f} KB")


if __name__ == "__main__":
    main()
