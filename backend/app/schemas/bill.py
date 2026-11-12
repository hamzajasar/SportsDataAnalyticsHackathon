"""Check a bill: the numbers a club types in from a bill, and what we derive from them.

- `ConfirmedBill` is the strict input the club sends.
- `BillReading` is the internal, lenient form the sanity checks run on (any field may be missing).
"""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.club import ClubRequest


class BillReading(BaseModel):
    """A bill's numbers for the sanity checks. Null means 'not given', never a guess."""

    kind: Literal["electricity", "fuel", "other"]
    period_year: int | None = None
    period_month: int | None = None  # month with most days of the billing period
    kwh_total: float | None = None  # electricity consumed in the period (all tariffs summed)
    amount_total_km: float | None = None  # total to pay, KM, VAT included
    unit_price_km_per_kwh: float | None = None  # printed energy price per kWh, if a single price
    litres: float | None = None
    fuel_type: Literal["diesel", "petrol", "lpg", "other"] | None = None
    confidence: Literal["high", "medium", "low"]
    unreadable_reason: str | None = None
    note: str | None = None


class ConfirmedBill(BaseModel):
    """The numbers the club typed in from its bill."""

    kind: Literal["electricity", "fuel"]
    period_year: int | None = Field(None, ge=2000, le=2100)
    period_month: int | None = Field(None, ge=1, le=12)
    kwh: float | None = Field(None, gt=0, le=1_000_000)
    amount_km: float | None = Field(None, gt=0, le=10_000_000)
    unit_price_km_per_kwh: float | None = Field(None, gt=0, le=10)
    litres: float | None = Field(None, gt=0, le=100_000)
    fuel_type: Literal["diesel", "petrol"] | None = None


class BillAnalyseRequest(ClubRequest):
    """Shared club profile (`club: null` = sample club) plus the confirmed bill."""

    bill: ConfirmedBill
    mean_temp_c: float | None = Field(
        None,
        ge=-40,
        le=45,
        description="Actual mean temperature of the bill month; default is the typical month",
    )


class WasteCheck(BaseModel):
    status: Literal["normal", "above", "high", "below", "unknown"]
    month: int
    actual_kwh: float
    expected_kwh: float
    difference_kwh: float
    difference_pct: float | None
    excess_kwh: float
    excess_km: float
    temperature_c: float
    temperature_source: str
    basis: str
    suggestions: list[str]  # ids, mapped to wording by the client / board text


class FuelCheck(BaseModel):
    fuel_type: str
    litres: float
    amount_km: float
    price_km_per_litre: float
    assumed_km_per_litre: float
    difference_pct: float


class PlanSummary(BaseModel):
    electricity_kwh_year: float
    electricity_km_year: float
    travel_km_cost_year: float
    total_saves_km_year: float
    total_saves_t_co2_year: float
    fee_drop_per_child_km: float
    top_actions: list[dict]


class PlanUpdate(BaseModel):
    before: PlanSummary
    after: PlanSummary
    scale_factor: float  # how the club's yearly electricity was scaled to match the bill
    annual_kwh_estimate: float | None = None
    price_km_per_kwh_used: float
    price_source: str
    price_source_id: Literal["unit_price", "total_per_kwh", "assumed", "fuel"]
    based_on: str  # honest label of how thin the evidence is


class BillAnalysis(BaseModel):
    kind: Literal["electricity", "fuel"]
    waste: WasteCheck | None = None
    fuel: FuelCheck | None = None
    plan: PlanUpdate
    board_text_bs: str
    warnings: list[str]
    illustrative_club: bool
