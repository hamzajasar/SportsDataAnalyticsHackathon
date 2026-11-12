from typing import Any, Literal

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


# ---- Club data from app/reference (draft shapes until the organisers' pack is integrated) ----


class Venue(BaseModel):
    id: str
    lat: float
    lon: float
    leisure: str | None
    sport: str | None
    name: str | None
    distance_km: float | None = None


class Source(BaseModel):
    id: str
    name: str
    use: str | None = None
    licence: str | None = None
    credit: str | None = None
    url: str | None = None
    file: str | None = None
    status: str | None = None


class CostAssumption(BaseModel):
    key: str
    value: float
    unit: str
    note: str | None = None
    source: str


class MonthlyValue(BaseModel):
    month: int
    value: float
    source: str


class Upgrade(BaseModel):
    """One upgrade the action plan can recommend (backend/app/reference/upgrades.json).

    Which fields are set depends on the kind of upgrade:
    - share of one electricity use (LED, insulation): cost_km + saves_share_of + share
    - solar: kwp + cost_km_per_kwp + self_use_share
    - travel (car-sharing): cost_km + cuts_car_trips_share
    """

    id: str
    name: str
    cost_km: float | None = None
    saves_share_of: str | None = None
    share: float | None = None
    kwp: float | None = None
    cost_km_per_kwp: float | None = None
    self_use_share: float | None = None
    cuts_car_trips_share: float | None = None
    note: str | None = None


class ClubAssumptions(BaseModel):
    costs: list[CostAssumption]
    upgrades: list[Upgrade]
    pv_yield_monthly: list[MonthlyValue]  # kWh per installed kWp
    temperature_monthly: list[MonthlyValue]  # mean °C


class MonthlySeries(BaseModel):
    unit: str
    months: list[MonthlyValue]
    annual: float | None = None  # sum (PV) or mean (temperature)
    source: str


class Distance(BaseModel):
    straight_km: float
    road_km_estimate: float
    circuity_factor: float
    note: str


class ShareSuggestions(BaseModel):
    radius_km: float
    shared_pitch: list[Venue]
    carpool_partners: list[Venue]
    note: str


# ---- Action plan (shape = Lane A's services/actions.py output) ----


class Baseline(BaseModel):
    electricity_kwh: float
    electricity_km: float
    electricity_t_co2: float
    travel_km_driven: float
    travel_km_cost: float
    travel_t_co2: float
    grid_gco2_per_kwh: float
    grid_year: int
    club_pays_electricity: bool = True
    club_electricity_km: float = Field(description="Electricity cost the club itself pays")
    heating_type: str = "electric"
    illustrative_club: bool = Field(description="True when calculated for the sample club")


class Action(BaseModel):
    id: str
    name: str
    cost_km: float
    saves_km_year: float
    saves_kg_co2_year: float
    saves_kwh_year: float
    payback_years: float | None
    basis: str
    owner: Literal["club", "facility_owner", "families"] = Field(
        "club", description="Who takes (and saves from) this action"
    )
    counts_for_club: bool = Field(True, description="Included in the club's totals and fee drop")


class ActionPlanAssumptions(BaseModel):
    electricity_price_km_per_kwh: float
    grid_gco2_per_kwh: float
    grid_year: int
    illustrative_club: bool


class ActionPlan(BaseModel):
    actions: list[Action]  # sorted by payback, free actions first
    total_saves_km_year: float
    total_saves_t_co2_year: float
    fee_drop_per_child_km: float
    facility_owner_saves_km_year: float = Field(
        0, description="Savings for the facility owner when the club doesn't pay electricity"
    )
    notes: list[str] = Field(default_factory=list, description="Plain-language caveats to show")
    children: int
    assumptions: ActionPlanAssumptions
    illustrative_club: bool = Field(description="True when calculated for the sample club")
