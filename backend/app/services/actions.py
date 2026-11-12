"""Heating-vs-weather model and ranked savings actions for a community club.

Pure functions: every number returned carries the inputs/assumptions it came from, so the UI can
show *how* it was calculated. The sample club is ILLUSTRATIVE (no data pack);
all inputs can be overridden.

  CO2 (kg)         = kWh x grid gCO2/kWh / 1000
  trip CO2 (kg)    = km x 2 x vehicles x kg per vehicle-km
  payback (years)  = cost / yearly saving (KM)
  fee drop / child = total yearly saving / children
"""

import csv
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from app.i18n import Lang, M, num, pct, t
from app.services.emissions import factor, grid_intensity

REFERENCE_DIR = Path(__file__).resolve().parents[1] / "reference"
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
HEATING_BASE_C = 15.0  # below this outdoor mean temperature the building needs heating (assumption)


@lru_cache
def _json(name: str) -> dict | list:
    return json.loads((REFERENCE_DIR / name).read_text(encoding="utf-8"))


def sample_club() -> dict:
    return dict(_json("sample_club.json"))


def upgrades() -> list[dict]:
    return list(_json("upgrades.json"))


@lru_cache
def _csv(name: str) -> list[dict]:
    with open(REFERENCE_DIR / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def monthly_temps() -> list[float]:
    rows = sorted(_csv("sarajevo_temperature.csv"), key=lambda r: int(r["month"]))
    return [float(r["mean_temp_c"]) for r in rows]


def cost_assumptions() -> dict[str, float]:
    return {r["key"]: float(r["value"]) for r in _csv("cost_assumptions.csv")}


def pv_kwh_per_kwp_year() -> float:
    return sum(float(r["kwh_per_kwp"]) for r in _csv("pv_yield_sarajevo.csv"))


# ---- Heating vs weather --------------------------------------------------------------------


def heating_degree_days(temps: list[float], base: float = HEATING_BASE_C) -> list[float]:
    return [max(0.0, base - t) * d for t, d in zip(temps, DAYS, strict=True)]


def heating_profile(annual_heating_kwh: float, temps: list[float] | None = None) -> dict:
    """Spread a year's heating energy over months in proportion to heating degree days."""
    temps = temps or monthly_temps()
    hdd = heating_degree_days(temps)
    total = sum(hdd)
    kwh = [annual_heating_kwh * h / total for h in hdd] if total else [0.0] * 12
    return {
        "base_temp_c": HEATING_BASE_C,
        "monthly": [
            {"month": i + 1, "mean_temp_c": t, "hdd": round(h, 1), "heating_kwh": round(k, 0)}
            for i, (t, h, k) in enumerate(zip(temps, hdd, kwh, strict=True))
        ],
        "method": "annual heating kWh x month's share of heating degree days (base 15 C)",
    }


def fit_heating(monthly_kwh: list[float], temps: list[float] | None = None) -> dict:
    """OLS of monthly kWh on heating degree days. Use with REAL meter data: reports R^2 and
    residuals so months that use more than the weather explains (possible waste) stand out."""
    temps = temps or monthly_temps()
    x = np.array(heating_degree_days(temps))
    y = np.array(monthly_kwh, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    pred = intercept + slope * x
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return {
        "baseload_kwh_per_month": round(float(intercept), 1),
        "kwh_per_hdd": round(float(slope), 3),
        "r_squared": round(1 - ss_res / ss_tot, 3) if ss_tot else None,
        "months": [
            {
                "month": i + 1,
                "actual_kwh": float(a),
                "expected_kwh": round(float(p), 1),
                "residual_kwh": round(float(a - p), 1),
            }
            for i, (a, p) in enumerate(zip(y, pred, strict=True))
        ],
    }


# ---- Baseline and ranked actions -----------------------------------------------------------


def _travel_km(club: dict) -> float:
    t = club["travel"]
    return club["teams"] * t["away_trips_per_team_year"] * t["avg_one_way_km"] * 2


def baseline(
    club: dict | None = None, country: str = "BIH", costs: dict[str, float] | None = None
) -> dict:
    club = club or sample_club()
    c = {**cost_assumptions(), **(costs or {})}
    gi = grid_intensity(country)
    kwh = sum(club["electricity_kwh_year"].values())
    km = _travel_km(club)
    veh = club["travel"]["vehicles_per_trip"]
    kg_per_km = {
        "car": factor("car_average")["kg_co2e"],
        "minibus": factor("van_average")["kg_co2e"],
    }
    pays = club.get("pays_electricity", True)
    electricity_km = round(kwh * c["electricity_price"])
    return {
        "electricity_kwh": kwh,
        "electricity_km": electricity_km,  # the facility's bill, whoever pays it
        "club_pays_electricity": pays,
        "club_electricity_km": electricity_km if pays else 0,
        "heating_type": club.get("heating_type", "electric"),
        "electricity_t_co2": round(kwh * gi.gco2_per_kwh / 1e6, 1),
        "travel_km_driven": km * sum(veh.values()),
        "travel_km_cost": round(sum(km * n * c[f"fuel_cost_{v}"] for v, n in veh.items())),
        "travel_t_co2": round(sum(km * n * kg_per_km[v] for v, n in veh.items()) / 1000, 1),
        "grid_gco2_per_kwh": gi.gco2_per_kwh,
        "grid_year": gi.year,
    }


def rank_actions(
    club: dict | None = None,
    country: str = "BIH",
    price_kwh: float | None = None,
    costs: dict[str, float] | None = None,
    lang: Lang = "en",
) -> dict:
    """Actions with yearly KM and CO2 saved and payback, sorted by payback (free ones first).

    `costs` overrides rows of cost_assumptions.csv (e.g. a price read from the club's own bill).
    """
    club = club or sample_club()
    c = {**cost_assumptions(), **(costs or {})}
    price = price_kwh if price_kwh is not None else c["electricity_price"]
    gi = grid_intensity(country)
    kg_per_kwh = gi.gco2_per_kwh / 1000
    el = club["electricity_kwh_year"]
    km = _travel_km(club)
    pays = club.get("pays_electricity", True)
    heating = club.get("heating_type", "electric")
    club_kwh = sum(el.values())
    rows = []
    for u in upgrades():
        if "kwp" in u:  # solar, sized to the club's own use
            kwp = u["kwp"]
            if u.get("reference_kwh"):
                kwp = round(u["kwp"] * club_kwh / u["reference_kwh"])
                kwp = min(max(kwp, u.get("min_kwp", 0)), u.get("max_kwp", kwp)) if club_kwh else 0
            cost = kwp * u["cost_km_per_kwp"]
            produced_used = kwp * pv_kwh_per_kwp_year() * u["self_use_share"]
            # A club can't save more electricity than it actually buys.
            kwh_saved = min(produced_used, club_kwh)
            basis = t(
                "basis.solar",
                lang,
                kwp=kwp,
                yield_=num(pv_kwh_per_kwp_year(), lang),
                self_use=pct(u["self_use_share"], lang),
            )
            if kwh_saved < produced_used:
                basis += t("basis.solar_capped", lang, kwh=num(club_kwh, lang))
            row = _row(u, cost, kwh_saved * price, kwh_saved * kg_per_kwh, kwh_saved, basis)
            row["name"] = t("action.solar", lang, kwp=kwp)
            row["_electricity"] = True
        elif "cuts_car_trips_share" in u:
            car_km = km * club["travel"]["vehicles_per_trip"]["car"] * u["cuts_car_trips_share"]
            basis = t(
                "basis.carshare",
                lang,
                share=pct(u["cuts_car_trips_share"], lang),
                km=num(car_km, lang),
            )
            row = _row(
                u,
                u["cost_km"],
                car_km * c["fuel_cost_car"],
                car_km * factor("car_average")["kg_co2e"],
                0.0,
                basis,
            )
            row["_electricity"] = False
        elif "kits_per_child_year" in u:  # saves money for families, not the club
            swapped = club["children"] * u["kits_per_child_year"] * u["swap_share"]
            kg = swapped * u["kg_per_kit"]
            co2 = kg * (
                factor("material_clothing_new")["kg_co2e"]
                - factor("material_clothing_reused")["kg_co2e"]
            )
            basis = t(
                "basis.kit",
                lang,
                kits=num(swapped, lang),
                price=num(u["kit_price_km"], lang),
                kg=num(u["kg_per_kit"], lang, 1),
            )
            row = _row(u, u["cost_km"], swapped * u["kit_price_km"], co2, 0.0, basis)
            row["_electricity"] = False
            row["owner"] = "families"
        else:  # a share of one electricity use (LED, insulation, timers, setpoint)
            use = el[u["saves_share_of"]]
            cost = u["cost_km"]
            if u.get("reference_kwh"):
                cost = cost * use / u["reference_kwh"]
            kwh_saved = use * u["share"]
            basis = t(
                "basis.share_of",
                lang,
                share=pct(u["share"], lang),
                use=t(f"use.{u['saves_share_of']}", lang),
                kwh=num(use, lang),
            )
            row = _row(u, cost, kwh_saved * price, kwh_saved * kg_per_kwh, kwh_saved, basis)
            row["_electricity"] = True
        if f"action.{u['id']}" in M and "kwp" not in u:
            row["name"] = t(f"action.{u['id']}", lang)
        rows.append(row)

    # Who acts: electricity actions belong to whoever pays the electricity bill.
    for r in rows:
        is_electricity = r.pop("_electricity")
        if "owner" not in r:
            r["owner"] = "facility_owner" if is_electricity and not pays else "club"
        r["counts_for_club"] = r["owner"] == "club"
        r["cost_type"] = (
            "free" if r["cost_km"] == 0 else "low" if r["cost_km"] <= 1000 else "investment"
        )

    # Hide actions that don't apply to this club (e.g. insulation of an electric heater it doesn't
    # have, LED when it has no floodlights): they'd show up as "free" with no saving.
    rows = [r for r in rows if r["saves_km_year"] > 0]
    rows.sort(key=lambda r: (r["payback_years"] is None, r["payback_years"] or 0))
    mine = [r for r in rows if r["counts_for_club"]]
    total_km = sum(r["saves_km_year"] for r in mine)
    notes = []
    if not pays:
        notes.append(t("note.not_paying", lang))
    if heating != "electric":
        notes.append(t("note.heating_not_electric", lang, kind=t(f"heating.{heating}", lang)))
    return {
        "actions": rows,
        "total_saves_km_year": total_km,
        "total_saves_t_co2_year": round(sum(r["saves_kg_co2_year"] for r in mine) / 1000, 1),
        "fee_drop_per_child_km": round(total_km / club["children"], 1),
        "facility_owner_saves_km_year": sum(
            r["saves_km_year"] for r in rows if r["owner"] == "facility_owner"
        ),
        "families_save_km_year": sum(r["saves_km_year"] for r in rows if r["owner"] == "families"),
        "notes": notes,
        "children": club["children"],
        "assumptions": {
            "electricity_price_km_per_kwh": price,
            "grid_gco2_per_kwh": gi.gco2_per_kwh,
            "grid_year": gi.year,
            "illustrative_club": True,
        },
    }


def _row(u: dict, cost: float, km_saved: float, co2_kg: float, kwh: float, basis: str) -> dict:
    return {
        "id": u["id"],
        "name": u["name"],
        "cost_km": round(cost),
        "saves_km_year": round(km_saved),
        "saves_kg_co2_year": round(co2_kg),
        "saves_kwh_year": round(kwh),
        "payback_years": round(cost / km_saved, 1) if km_saved > 0 else None,
        "basis": basis,
    }
