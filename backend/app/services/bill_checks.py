"""Sanity checks on an electricity bill or fuel receipt typed in by the club.

Catches typos and implausible values (future dates, impossible kWh, unusual prices) before the
numbers update the club's plan.
"""

from datetime import date

from app.i18n import Lang, num, t
from app.schemas.bill import BillReading


def effective_price(r: BillReading) -> float | None:
    """All-in KM per kWh: total paid divided by kWh (includes fixed charges)."""
    if r.amount_total_km and r.kwh_total:
        return r.amount_total_km / r.kwh_total
    return None


def plausibility_warnings(
    r: BillReading, today: date | None = None, lang: Lang = "en"
) -> list[str]:
    """Sanity checks on a bill's numbers: a typo should be caught before it is used."""
    today = today or date.today()
    w: list[str] = []
    if r.kind == "other":
        w.append(r.unreadable_reason or t("check.other", lang))
        return w
    if r.confidence == "low":
        w.append(t("check.uncertain", lang))
    if r.period_month is not None and not 1 <= r.period_month <= 12:
        w.append(t("check.bad_month", lang))
    known = r.period_year is not None and r.period_month is not None
    if known and (r.period_year, r.period_month) > (today.year, today.month):
        w.append(t("check.future", lang))
    if r.kind == "electricity":
        if r.kwh_total is None:
            w.append(t("check.no_kwh", lang))
        elif not 0 < r.kwh_total <= 100_000:
            w.append(t("check.kwh_implausible", lang))
        price = effective_price(r)
        if price is not None and not 0.05 <= price <= 1.0:
            w.append(t("check.price_unusual", lang, price=num(price, lang, 2)))
        if r.unit_price_km_per_kwh is not None and not 0.03 <= r.unit_price_km_per_kwh <= 0.6:
            w.append(t("check.unit_price_unusual", lang))
    if r.kind == "fuel":
        if r.litres is None or r.amount_total_km is None:
            w.append(t("check.fuel_missing", lang))
        else:
            per_litre = r.amount_total_km / r.litres if r.litres else 0
            if not 1.5 <= per_litre <= 6.0:
                w.append(t("check.per_litre_unusual", lang, price=num(per_litre, lang, 2)))
        if r.fuel_type in (None, "other", "lpg"):
            w.append(t("check.fuel_type", lang))
    return w
