"""Club profile: the shared input format for every club calculation (baseline, actions, energy,
travel, affordability). Mirrors backend/app/reference/sample_club.json.

Send `ClubRequest` as the POST body; `club: null` means "use the illustrative sample club".
"""

from pydantic import BaseModel, Field


class Electricity(BaseModel):
    """Yearly electricity use in kWh, split by what it is used for."""

    floodlights: float = Field(ge=0, le=10_000_000)
    heating: float = Field(ge=0, le=10_000_000)
    hall_and_other: float = Field(ge=0, le=10_000_000)


class Vehicles(BaseModel):
    """Vehicles used for one away trip of one team."""

    minibus: int = Field(ge=0, le=20)
    car: int = Field(ge=0, le=50)


class Travel(BaseModel):
    away_trips_per_team_year: int = Field(ge=0, le=200)
    avg_one_way_km: float = Field(ge=0, le=2000)
    vehicles_per_trip: Vehicles


class ClubProfile(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=80)
    lat: float = Field(ge=42, le=46)  # Bosnia and Herzegovina
    lon: float = Field(ge=15, le=20)
    children: int = Field(gt=0, le=100_000)
    teams: int = Field(gt=0, le=500)
    electricity_kwh_year: Electricity
    travel: Travel


class ClubRequest(BaseModel):
    """POST body for club calculations. Omit `club` to use the sample club."""

    club: ClubProfile | None = None
    electricity_price_km_per_kwh: float | None = Field(
        None, gt=0, le=5, description="Override the sourced electricity price (KM/kWh)"
    )
