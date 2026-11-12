"""Action plan for a club: baseline costs/CO2 and upgrades ranked by payback.

Served by the live model in `services/actions.py` (sourced prices, Ember grid factor, PVGIS yield).
`club=None` uses the ILLUSTRATIVE sample club (there was no organiser data pack); pass a club
profile (schemas/club.py, as a dict) to calculate for a real club.
"""

from app.i18n import Lang
from app.services import actions


def baseline(club: dict | None = None) -> dict:
    return {**actions.baseline(club), "illustrative_club": club is None}


def action_plan(club: dict | None = None, price: float | None = None, lang: Lang = "en") -> dict:
    plan = actions.rank_actions(club, price_kwh=price, lang=lang)
    # The model always marks its club as illustrative; only the sample club actually is.
    plan["assumptions"] = {**plan["assumptions"], "illustrative_club": club is None}
    return {**plan, "illustrative_club": club is None}
