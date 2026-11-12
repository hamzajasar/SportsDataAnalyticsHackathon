"""Club advisor: turn one confirmed bill into a waste check, an updated plan and a board text.

Electricity bill
  1. price      = printed unit price, else bill total / kWh, else the assumed Eurostat price
  2. waste      = actual kWh vs what the club's own yearly figures predict for that month
  3. plan       = the club's yearly electricity scaled by (actual / expected for the month),
                  re-ranked with the bill's price; shown next to the plan before the bill
Fuel receipt
  price per litre replaces the assumed pump price in the cost of one vehicle-km; plan re-ranked.

One bill is thin evidence, and the output says so. Nothing here calls an AI: the AI only reads the
photo, and a person confirms the numbers first.
"""

from datetime import date

from app.schemas.bill import BillReading
from app.services import actions, board_text, waste
from app.services.bill_reader import plausibility_warnings

SCALE_MIN, SCALE_MAX = 0.25, 4.0  # one bill may not move the yearly estimate more than this


class BillInputError(ValueError):
    """The confirmed bill lacks what this kind of analysis needs."""


def _plan_summary(club: dict, costs: dict[str, float] | None = None) -> dict:
    base = actions.baseline(club, costs=costs)
    plan = actions.rank_actions(club, costs=costs, price_kwh=(costs or {}).get("electricity_price"))
    return {
        "electricity_kwh_year": base["electricity_kwh"],
        "electricity_km_year": base["electricity_km"],
        "travel_km_cost_year": base["travel_km_cost"],
        "total_saves_km_year": plan["total_saves_km_year"],
        "total_saves_t_co2_year": plan["total_saves_t_co2_year"],
        "fee_drop_per_child_km": plan["fee_drop_per_child_km"],
        "top_actions": [
            {
                "id": a["id"],
                "name": a["name"],
                "cost_km": a["cost_km"],
                "saves_km_year": a["saves_km_year"],
                "payback_years": a["payback_years"],
            }
            for a in plan["actions"][:3]
        ],
    }


def _electricity_price(bill: dict, assumed: float) -> tuple[float, str]:
    if bill.get("unit_price_km_per_kwh"):
        return bill["unit_price_km_per_kwh"], "unit_price"
    if bill.get("amount_km") and bill.get("kwh"):
        return bill["amount_km"] / bill["kwh"], "total_per_kwh"
    return assumed, "assumed"


PRICE_SOURCES = {
    "unit_price": "price per kWh printed on the bill",
    "total_per_kwh": "bill total divided by kWh (includes fixed charges, so savings from "
    "using less electricity may be slightly overstated)",
    "assumed": "assumed Eurostat price for BiH (the bill gave no price)",
}


def _electricity(club: dict, bill: dict, mean_temp_c: float | None) -> dict:
    kwh, month = bill.get("kwh"), bill.get("period_month")
    if not kwh or not month:
        raise BillInputError("An electricity bill needs the kWh and the billing month.")
    assumed = actions.cost_assumptions()["electricity_price"]
    price, price_key = _electricity_price(bill, assumed)

    check = waste.check_month(club, month, kwh, price, mean_temp_c)
    expected = waste.expected_month_kwh(club, month, mean_temp_c)["total"]
    warnings: list[str] = []
    raw_scale = kwh / expected if expected > 0 else 1.0
    scale = min(SCALE_MAX, max(SCALE_MIN, raw_scale))
    if scale != raw_scale:
        warnings.append(
            f"The bill is far from the club's profile (x{raw_scale:.2f}); the yearly estimate was "
            f"limited to x{scale:.2f}. Check the kWh and the club's yearly figures."
        )
    scaled = {
        **club,
        "electricity_kwh_year": {k: v * scale for k, v in club["electricity_kwh_year"].items()},
    }
    before = _plan_summary(club)
    after = _plan_summary(scaled, {"electricity_price": price})
    return {
        "waste": check,
        "plan": {
            "before": before,
            "after": after,
            "scale_factor": round(scale, 3),
            "annual_kwh_estimate": after["electricity_kwh_year"],
            "price_km_per_kwh_used": round(price, 4),
            "price_source": PRICE_SOURCES[price_key],
            "price_source_id": price_key,
            "based_on": (
                f"One bill (month {month}): the club's yearly electricity is scaled from this "
                "single month. Each further bill makes the estimate firmer."
            ),
        },
        "warnings": warnings,
    }


def _fuel(club: dict, bill: dict) -> dict:
    litres, amount, ftype = bill.get("litres"), bill.get("amount_km"), bill.get("fuel_type")
    if not (litres and amount and ftype):
        raise BillInputError("A fuel receipt needs litres, the amount and the fuel type.")
    c = actions.cost_assumptions()
    price_l = amount / litres
    assumed = c[f"{ftype}_price"]
    # petrol -> the club's cars, diesel -> its minibus (as in cost_assumptions.csv)
    vehicle = "car" if ftype == "petrol" else "minibus"
    override = {f"fuel_cost_{vehicle}": price_l * c[f"fuel_use_{vehicle}"] / 100}
    before, after = _plan_summary(club), _plan_summary(club, override)
    return {
        "fuel": {
            "fuel_type": ftype,
            "litres": litres,
            "amount_km": amount,
            "price_km_per_litre": round(price_l, 3),
            "assumed_km_per_litre": assumed,
            "difference_pct": round((price_l / assumed - 1) * 100, 1),
        },
        "plan": {
            "before": before,
            "after": after,
            "scale_factor": 1.0,
            "annual_kwh_estimate": None,
            "price_km_per_kwh_used": c["electricity_price"],
            "price_source": "electricity price unchanged (a fuel receipt says nothing about it)",
            "price_source_id": "fuel",
            "based_on": (
                f"One {ftype} receipt: the pump price replaces the assumed one in the cost of "
                f"a {vehicle} kilometre."
            ),
        },
        "warnings": [],
    }


def analyse_bill(
    club: dict | None,
    bill: dict,
    mean_temp_c: float | None = None,
    today: date | None = None,
) -> dict:
    illustrative = club is None
    club = club or actions.sample_club()
    reading = BillReading(
        kind=bill["kind"],
        period_year=bill.get("period_year"),
        period_month=bill.get("period_month"),
        kwh_total=bill.get("kwh"),
        amount_total_km=bill.get("amount_km"),
        unit_price_km_per_kwh=bill.get("unit_price_km_per_kwh"),
        litres=bill.get("litres"),
        fuel_type=bill.get("fuel_type"),
        confidence="high",  # the person confirmed it
    )
    warnings = plausibility_warnings(reading, today)
    result = (
        _electricity(club, bill, mean_temp_c)
        if bill["kind"] == "electricity"
        else _fuel(club, bill)
    )
    warnings += result.pop("warnings")
    analysis = {
        "kind": bill["kind"],
        "waste": result.get("waste"),
        "fuel": result.get("fuel"),
        "plan": result["plan"],
        "warnings": warnings,
        "illustrative_club": illustrative,
    }
    analysis["board_text_bs"] = board_text.decision_text_bs(analysis, club, bill, today)
    return analysis
