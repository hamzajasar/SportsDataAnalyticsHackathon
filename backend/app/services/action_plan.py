"""Action plan for a club: baseline costs/CO2 and upgrades ranked by payback.

Served by the live model in `services/actions.py` (sample club, sourced prices, Ember grid
factor, PVGIS yield). The club itself is ILLUSTRATIVE: there was no organiser data pack.
"""

from app.services import actions


def baseline() -> dict:
    return {**actions.baseline(), "example": False}


def action_plan() -> dict:
    return {**actions.rank_actions(), "example": False}
