"""Action plan for a club: baseline costs/CO2 and upgrades ranked by payback.

EXAMPLE DATA for now (so the frontend isn't blocked). The numbers below are the real output of
Lane A's model (`services/actions.py` on branch feature/action-plan-model) for the illustrative
sample club. When that branch is merged into dev, replace the two functions' bodies with:

    from app.services import actions
    return {**actions.baseline(), "example": False}
    return {**actions.rank_actions(), "example": False}

The response shape is identical, so the API and frontend need no change.
"""

EXAMPLE_BASELINE = {
    "electricity_kwh": 52000,
    "electricity_km": 15132,
    "electricity_t_co2": 29.7,
    "travel_km_driven": 32400,
    "travel_km_cost": 8537,
    "travel_t_co2": 6.1,
    "grid_gco2_per_kwh": 570.64,
    "grid_year": 2025,
}

EXAMPLE_PLAN = {
    "actions": [
        {"id": "carshare", "name": "Car-sharing, fill the minibus", "cost_km": 0,
         "saves_km_year": 2187, "saves_kg_co2_year": 1626, "saves_kwh_year": 0,
         "payback_years": 0.0, "basis": "40% fewer car-km (9720 km)"},
        {"id": "led", "name": "LED floodlights", "cost_km": 9000, "saves_km_year": 3841,
         "saves_kg_co2_year": 7532, "saves_kwh_year": 13200, "payback_years": 2.3,
         "basis": "60% of floodlights (22000 kWh)"},
        {"id": "solar", "name": "Solar roof 20 kWp", "cost_km": 24000, "saves_km_year": 5592,
         "saves_kg_co2_year": 10966, "saves_kwh_year": 19218, "payback_years": 4.3,
         "basis": "20 kWp x 1201 kWh/kWp (PVGIS) x 80% used on site"},
        {"id": "insul", "name": "Insulation + heat pump", "cost_km": 15000, "saves_km_year": 2328,
         "saves_kg_co2_year": 4565, "saves_kwh_year": 8000, "payback_years": 6.4,
         "basis": "40% of heating (20000 kWh)"},
    ],
    "total_saves_km_year": 13948,
    "total_saves_t_co2_year": 24.7,
    "fee_drop_per_child_km": 77.5,
    "children": 180,
    "assumptions": {
        "electricity_price_km_per_kwh": 0.291,
        "grid_gco2_per_kwh": 570.64,
        "grid_year": 2025,
        "illustrative_club": True,
    },
}  # fmt: skip


def baseline() -> dict:
    return {**EXAMPLE_BASELINE, "example": True}


def action_plan() -> dict:
    return {**EXAMPLE_PLAN, "example": True}
