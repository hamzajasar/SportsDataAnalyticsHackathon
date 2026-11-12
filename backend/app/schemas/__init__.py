from typing import Any

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str
    database: bool


class DatasetInfo(BaseModel):
    id: str
    name: str
    format: str
    size_bytes: int


class DatasetPreview(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    total_rows: int


class ColumnSummary(BaseModel):
    name: str
    type: str
    null_pct: float
    approx_unique: int
    min: str | None
    max: str | None
    mean: float | None
    likely_key: bool


class DatasetSummary(BaseModel):
    dataset_id: str
    rows: int
    columns: list[ColumnSummary]


# ---- Sustainability (Topic 6) ----


class IntensityPoint(BaseModel):
    year: int
    gco2_per_kwh: float


class IntensitySeries(BaseModel):
    entity: str
    code: str
    points: list[IntensityPoint]


class ElectricityMix(BaseModel):
    entity: str
    year: int
    shares_pct: dict[str, float]
    source: str


class ElectricityEstimate(BaseModel):
    kwh: float
    kg_co2e: float
    country: str
    year: int
    gco2_per_kwh: float
    source: str


class EmissionFactor(BaseModel):
    category: str
    key: str
    unit: str
    kg_co2e: float
    source: str


class AmountEstimate(BaseModel):
    key: str
    unit: str
    kg_co2e: float
    amount: float
    total_kg_co2e: float
    source: str


class TripRequest(BaseModel):
    distance_km: float = Field(gt=0, le=5000, description="One-way distance")
    people: int = Field(gt=0, le=200)
    round_trip: bool = True
    car_occupancy: int = Field(3, ge=1, le=7)
    car_type: str = "car_average"


class TripOption(BaseModel):
    mode: str
    label: str
    vehicles: int | None
    kg_co2e: float
    saving_vs_worst_kg: float
    assumption: str


class TripComparison(BaseModel):
    distance_km: float
    total_km: float
    people: int
    options: list[TripOption]
    source: str
