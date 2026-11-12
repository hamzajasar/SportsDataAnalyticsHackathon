"""Request/response shapes for the season-travel calculator."""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.club import ClubRequest


class SeasonTravelRequest(ClubRequest):
    """Shared club profile (`club: null` = sample club) plus the travel options.

    `electricity_price_km_per_kwh` is part of the shared format but unused here: travel costs
    use fuel and coach-hire prices.
    """

    people_per_trip: int = Field(18, ge=1, le=200, description="Squad + staff per away trip")
    share_with_partner: bool = Field(False, description="One coach shared by two clubs")


class SeasonTravelOption(BaseModel):
    mode: Literal["current", "cars", "minibus", "coach"]
    label: str
    vehicles: dict[str, int]
    cost_km: float
    co2_kg: float
    saving_vs_current_cost_km: float
    saving_vs_current_co2_kg: float


class SeasonTravel(BaseModel):
    trips: int
    round_trip_km: float
    people_per_trip: int
    share_with_partner: bool
    shared_with: list[str]
    note: str | None = None
    options: list[SeasonTravelOption]
    cheapest: str
    lowest_co2: str
    assumptions: dict
