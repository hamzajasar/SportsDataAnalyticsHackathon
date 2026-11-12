"""Affordability tab: cost per child and fee drop per action (POST /api/club/affordability)."""

from pydantic import BaseModel


class AffordabilityAction(BaseModel):
    id: str
    name: str
    cost_km: float
    saves_km_year: float
    fee_drop_per_child_km: float
    payback_years: float | None


class Affordability(BaseModel):
    children: int
    running_cost_km_year: float
    electricity_km_year: float
    travel_km_year: float
    cost_per_child_km: float
    actions: list[AffordabilityAction]  # same order as the action plan (by payback)
    total_fee_drop_per_child_km: float
    cost_per_child_after_km: float
    families_save_per_child_km: float = 0  # e.g. kit swap: money families keep
    saving_share_pct: float
    electricity_price_km_per_kwh: float
    scope: str
    note: str
    illustrative_club: bool
