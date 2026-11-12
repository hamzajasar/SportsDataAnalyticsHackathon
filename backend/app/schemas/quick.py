"""Quick start: 5 easy questions -> full club profile (POST /api/club/quick)."""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.club import ClubProfile, HeatingType


class City(BaseModel):
    city: str
    lat: float
    lon: float
    source: str


class QuickClubInput(BaseModel):
    """What a volunteer knows. Only city, children and teams are required."""

    name: str | None = Field(None, max_length=120)
    city: str = Field(min_length=1, max_length=80, description="A city from GET /api/cities")
    lat: float | None = Field(None, ge=42, le=46, description="Optional exact location")
    lon: float | None = Field(None, ge=15, le=20)
    children: int = Field(gt=0, le=100_000)
    teams: int = Field(gt=0, le=500)
    pays_electricity: bool = True
    monthly_bill_km: float | None = Field(None, ge=0, le=1_000_000, description="Average KM/month")
    yearly_kwh: float | None = Field(
        None, ge=0, le=10_000_000, description="If known (overrides bill)"
    )
    heating_type: HeatingType = "unknown"
    away_games_per_team: int | None = Field(None, ge=0, le=200, description="Per season")
    avg_one_way_km: float | None = Field(None, ge=0, le=2000)
    transport: Literal["cars", "minibus", "mixed"] = "mixed"


class QuickClubResult(BaseModel):
    club: ClubProfile  # send this as {"club": ...} to every /api/club/* endpoint
    estimated: list[str] = Field(description="Profile parts we estimated (not given by the club)")
    notes: list[str] = Field(description="Plain-language explanation of every estimate")
