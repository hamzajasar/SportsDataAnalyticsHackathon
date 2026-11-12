"""Waste detector: is this month's electricity bill higher than the weather explains?

expected kWh (month) = floodlights/12 + hall and other/12 + yearly heating x the month's
                       share of heating degree days (Sarajevo temperature, Open-Meteo)
difference           = actual / expected - 1

Same month profile as services/energy.py. It uses the typical Sarajevo temperature of the month
unless the caller supplies the real one, so a cold month is not mistaken for waste when the
real temperature is passed in. A flag means "worth checking", never a diagnosis.
"""

from app.services import actions

NORMAL_BAND_PCT = 10.0  # within +/- this: normal
HIGH_PCT = 25.0  # above this: high

SUGGESTIONS = {
    "floodlights": "Check floodlight timers and whether lights stay on after training.",
    "heating": "Check the heating set-point and whether unused rooms or the hall are heated.",
    "baseload": "Compare with last month's bill and read the meter to rule out a billing error.",
}


def expected_month_kwh(club: dict, month: int, mean_temp_c: float | None = None) -> dict:
    """What the club's own yearly figures predict for `month` (1-12)."""
    el = club["electricity_kwh_year"]
    temps = actions.monthly_temps()
    hdd_year = sum(actions.heating_degree_days(temps))
    temp = temps[month - 1] if mean_temp_c is None else mean_temp_c
    hdd_month = max(0.0, actions.HEATING_BASE_C - temp) * actions.DAYS[month - 1]
    heating = el["heating"] * hdd_month / hdd_year if hdd_year else 0.0
    flood, hall = el["floodlights"] / 12, el["hall_and_other"] / 12
    return {
        "total": flood + hall + heating,
        "heating": heating,
        "temperature_c": temp,
        "temperature_source": (
            "typical Sarajevo temperature for the month (Open-Meteo 2024-2025)"
            if mean_temp_c is None
            else "temperature supplied for the bill month"
        ),
    }


def check_month(
    club: dict, month: int, kwh: float, price_km_per_kwh: float, mean_temp_c: float | None = None
) -> dict:
    exp = expected_month_kwh(club, month, mean_temp_c)
    expected = exp["total"]
    diff = kwh - expected
    pct = diff / expected * 100 if expected > 0 else None
    if pct is None:
        status = "unknown"
    elif pct > HIGH_PCT:
        status = "high"
    elif pct > NORMAL_BAND_PCT:
        status = "above"
    elif pct < -NORMAL_BAND_PCT:
        status = "below"
    else:
        status = "normal"

    suggestions: list[str] = []
    if status in ("above", "high"):
        suggestions.append("floodlights")
        if exp["heating"] > 0.25 * expected:  # a heating month: heating is a real suspect
            suggestions.append("heating")
        suggestions.append("baseload")
    excess = max(0.0, diff)
    return {
        "status": status,
        "month": month,
        "actual_kwh": round(kwh),
        "expected_kwh": round(expected),
        "difference_kwh": round(diff),
        "difference_pct": None if pct is None else round(pct, 1),
        "excess_kwh": round(excess),
        "excess_km": round(excess * price_km_per_kwh),
        "temperature_c": round(exp["temperature_c"], 1),
        "temperature_source": exp["temperature_source"],
        "basis": (
            "Expected = floodlights and hall spread evenly over 12 months + yearly heating "
            f"spread by heating degree days (base {actions.HEATING_BASE_C:.0f} °C), "
            "from the club's own yearly figures"
        ),
        "suggestions": suggestions,
    }
