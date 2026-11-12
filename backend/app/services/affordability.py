"""Affordability tab: what the club's running costs mean per child, and how much each action
could lower the membership fee.

  running cost (KM/yr)   = electricity kWh x price + away-travel fuel cost
  cost per child         = running cost / children
  fee drop per action    = action's yearly KM saving / children
  cost per child after   = cost per child - total fee drop (never below 0)

Scope: only electricity + away travel (not staff, pitch rent, kit…). Actions are estimated one by
one; doing several together saves a little less than the sum (e.g. LED lowers the use solar
offsets), so the "after" figure is an upper bound on the saving.
"""

from app.services import actions


def affordability(club: dict | None = None, price: float | None = None) -> dict:
    illustrative = club is None
    club = club or actions.sample_club()
    price = price if price is not None else actions.cost_assumptions()["electricity_price"]
    b = actions.baseline(club)
    plan = actions.rank_actions(club, price_kwh=price)
    children = club["children"]

    # Only costs the club itself pays (municipal facilities: electricity is the owner's bill).
    electricity_km = round(b["electricity_kwh"] * price) if b["club_pays_electricity"] else 0
    running = electricity_km + b["travel_km_cost"]
    per_child = running / children
    rows = [
        {
            "id": a["id"],
            "name": a["name"],
            "cost_km": a["cost_km"],
            "saves_km_year": a["saves_km_year"],
            "fee_drop_per_child_km": round(a["saves_km_year"] / children, 1),
            "payback_years": a["payback_years"],
        }
        for a in plan["actions"]
        if a["counts_for_club"]
    ]
    total_drop = plan["total_saves_km_year"] / children
    return {
        "children": children,
        "running_cost_km_year": running,
        "electricity_km_year": electricity_km,
        "travel_km_year": b["travel_km_cost"],
        "cost_per_child_km": round(per_child, 1),
        "actions": rows,
        "total_fee_drop_per_child_km": round(total_drop, 1),
        "cost_per_child_after_km": round(max(0.0, per_child - total_drop), 1),
        "families_save_per_child_km": round(plan["families_save_km_year"] / children, 1),
        "saving_share_pct": round(100 * plan["total_saves_km_year"] / running, 1) if running else 0,
        "electricity_price_km_per_kwh": price,
        "scope": "Electricity and away-travel fuel only (not staff, pitch rent or kit)",
        "note": (
            "Actions are estimated one by one; doing several together saves somewhat less than "
            "the sum, so 'after' is a best case."
        ),
        "illustrative_club": illustrative,
    }
