"""Energy tab: monthly electricity profile with optional solar (POST /api/club/energy)."""

from pydantic import BaseModel, Field

from app.schemas.club import ClubRequest


class EnergyRequest(ClubRequest):
    """Shared club profile (`club: null` = sample club) plus the solar size to test."""

    kwp: float = Field(0, ge=0, le=1000, description="Solar panels to add, in kWp (0 = none)")


class EnergyMonth(BaseModel):
    month: int
    mean_temp_c: float
    heating_kwh: float
    floodlights_kwh: float
    hall_kwh: float
    total_kwh: float
    solar_produced_kwh: float
    solar_used_kwh: float
    net_kwh: float  # bought from the grid
    cost_km: float
    co2_kg: float


class EnergyTotals(BaseModel):
    total_kwh: float
    solar_produced_kwh: float
    solar_used_kwh: float
    net_kwh: float
    cost_km: float
    co2_kg: float


class EnergyProfile(BaseModel):
    months: list[EnergyMonth]
    totals: EnergyTotals
    kwp: float
    solar_self_use_share: float
    electricity_price_km_per_kwh: float
    grid_gco2_per_kwh: float
    grid_year: int
    method: list[str]
    club_pays_electricity: bool = True
    heating_type: str = "electric"
    illustrative_club: bool
