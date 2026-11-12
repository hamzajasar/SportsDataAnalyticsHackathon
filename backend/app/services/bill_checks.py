"""Sanity checks on an electricity bill or fuel receipt typed in by the club.

Catches typos and implausible values (future dates, impossible kWh, unusual prices) before the
numbers update the club's plan.
"""

from datetime import date

from app.schemas.bill import BillReading


def effective_price(r: BillReading) -> float | None:
    """All-in KM per kWh: total paid divided by kWh (includes fixed charges)."""
    if r.amount_total_km and r.kwh_total:
        return r.amount_total_km / r.kwh_total
    return None


def plausibility_warnings(r: BillReading, today: date | None = None) -> list[str]:
    """Sanity checks on a bill's numbers: a typo should be caught before it is used."""
    today = today or date.today()
    w: list[str] = []
    if r.kind == "other":
        w.append(r.unreadable_reason or "This does not look like an electricity bill or receipt.")
        return w
    if r.confidence == "low":
        w.append("Some numbers are uncertain: check every number against the bill.")
    if r.period_month is not None and not 1 <= r.period_month <= 12:
        w.append("The billing month is not a valid month.")
    known = r.period_year is not None and r.period_month is not None
    if known and (r.period_year, r.period_month) > (today.year, today.month):
        w.append("The billing period is in the future: check the month and year.")
    if r.kind == "electricity":
        if r.kwh_total is None:
            w.append("No kWh found: type in the consumption from the bill.")
        elif not 0 < r.kwh_total <= 100_000:
            w.append("The kWh figure looks implausible for a club: check it.")
        price = effective_price(r)
        if price is not None and not 0.05 <= price <= 1.0:
            w.append(f"Total ÷ kWh is {price:.2f} KM/kWh, which looks unusual: check both numbers.")
        if r.unit_price_km_per_kwh is not None and not 0.03 <= r.unit_price_km_per_kwh <= 0.6:
            w.append("The printed price per kWh looks unusual: check it.")
    if r.kind == "fuel":
        if r.litres is None or r.amount_total_km is None:
            w.append("Litres or amount not found: type them in from the receipt.")
        else:
            per_litre = r.amount_total_km / r.litres if r.litres else 0
            if not 1.5 <= per_litre <= 6.0:
                w.append(f"{per_litre:.2f} KM per litre looks unusual: check litres and amount.")
        if r.fuel_type in (None, "other", "lpg"):
            w.append("Only diesel and petrol receipts can update the travel plan.")
    return w
