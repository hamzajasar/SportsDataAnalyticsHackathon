"""Energy tab: a club's electricity month by month, with optional solar.

heating kWh / month  = annual heating x month's share of heating degree days (Open-Meteo temps)
floodlights, hall    = annual / 12 (even spread — assumption, stated in `method`)
solar produced       = kWp x PVGIS kWh per kWp for that month
solar used on site   = min(produced x self-use share, that month's use)
net (bought) kWh     = use - solar used on site
cost (KM)            = net kWh x electricity price
CO2 (kg)             = net kWh x BiH grid gCO2/kWh / 1000
"""

from app.i18n import Lang, pct, t
from app.services import actions
from app.services.club_data import load_csv
from app.services.emissions import grid_intensity

DEFAULT_SELF_USE = 0.8  # share of solar output used on site (rest exported) — assumption


def _solar_self_use() -> float:
    solar = next((u for u in actions.upgrades() if "kwp" in u), None)
    return float(solar["self_use_share"]) if solar else DEFAULT_SELF_USE


def energy_profile(
    club: dict | None = None, kwp: float = 0, price: float | None = None, lang: Lang = "en"
) -> dict:
    illustrative = club is None
    club = club or actions.sample_club()
    el = club["electricity_kwh_year"]
    price = price if price is not None else actions.cost_assumptions()["electricity_price"]
    gi = grid_intensity("BIH")
    self_use = _solar_self_use()

    heating = actions.heating_profile(el["heating"])["monthly"]
    pv = load_csv("pv_yield").sort_values("month")["kwh_per_kwp"].tolist()

    months = []
    for i, h in enumerate(heating):
        flood = el["floodlights"] / 12
        hall = el["hall_and_other"] / 12
        heat = float(h["heating_kwh"])
        use = flood + hall + heat
        produced = kwp * float(pv[i])
        used = min(produced * self_use, use)
        net = use - used
        months.append(
            {
                "month": i + 1,
                "mean_temp_c": h["mean_temp_c"],
                "heating_kwh": round(heat),
                "floodlights_kwh": round(flood),
                "hall_kwh": round(hall),
                "total_kwh": round(use),
                "solar_produced_kwh": round(produced),
                "solar_used_kwh": round(used),
                "net_kwh": round(net),
                "cost_km": round(net * price),
                "co2_kg": round(net * gi.gco2_per_kwh / 1000),
            }
        )

    def total(key: str) -> float:
        return sum(m[key] for m in months)

    return {
        "months": months,
        "totals": {
            k: total(k)
            for k in (
                "total_kwh",
                "solar_produced_kwh",
                "solar_used_kwh",
                "net_kwh",
                "cost_km",
                "co2_kg",
            )
        },
        "kwp": kwp,
        "solar_self_use_share": self_use,
        "electricity_price_km_per_kwh": price,
        "grid_gco2_per_kwh": gi.gco2_per_kwh,
        "grid_year": gi.year,
        "method": [
            t("energy.heating", lang, base=f"{actions.HEATING_BASE_C:.0f}"),
            t("energy.even", lang),
            t("energy.solar", lang, self_use=pct(self_use, lang)),
            t("energy.sources", lang),
        ],
        "club_pays_electricity": club.get("pays_electricity", True),
        "heating_type": club.get("heating_type", "electric"),
        "illustrative_club": illustrative,
    }
