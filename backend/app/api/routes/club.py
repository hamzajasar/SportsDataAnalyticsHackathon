"""Club data, assumptions, venues and sources (from app/reference, shipped with the backend)."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.schemas import ActionPlan, Baseline, ClubAssumptions, MonthlySeries, Source, Venue
from app.schemas.club import ClubRequest
from app.schemas.travel import SeasonTravel, SeasonTravelRequest
from app.services import action_plan, travel
from app.services import club_data as svc

router = APIRouter(tags=["club"])


def _missing(e: FileNotFoundError) -> HTTPException:
    return HTTPException(503, str(e))


@router.get("/club/sample", response_model=dict[str, Any], operation_id="getSampleClub")
def sample_club() -> dict[str, Any]:
    """Illustrative sample club (placeholder until the organisers' pack is integrated)."""
    try:
        return svc.sample_club()
    except FileNotFoundError as e:
        raise _missing(e) from None


@router.get("/club/assumptions", response_model=ClubAssumptions, operation_id="getAssumptions")
def assumptions() -> ClubAssumptions:
    try:
        return ClubAssumptions(**svc.assumptions())
    except FileNotFoundError as e:
        raise _missing(e) from None


@router.get("/venues", response_model=list[Venue], operation_id="listVenues")
def venues(
    leisure: str | None = Query(None, pattern="^(pitch|stadium|sports_centre|sports_hall)$"),
    lat: float | None = Query(None, ge=42, le=46),
    lon: float | None = Query(None, ge=15, le=20),
    radius_km: float | None = Query(None, gt=0, le=500),
    limit: int = Query(5000, ge=1, le=5000),
) -> list[Venue]:
    if (lat is None) != (lon is None):
        raise HTTPException(422, "Give both lat and lon, or neither")
    near = (lat, lon) if lat is not None and lon is not None else None
    try:
        return [Venue(**v) for v in svc.venues(leisure, near, radius_km, limit)]
    except FileNotFoundError as e:
        raise _missing(e) from None


@router.get("/sources", response_model=list[Source], operation_id="listSources")
def sources() -> list[Source]:
    """Every data source with licence + credit line (for the Methodology page and final slide)."""
    try:
        return [Source(**s) for s in svc.sources()]
    except FileNotFoundError as e:
        raise _missing(e) from None


@router.get("/climate/temperature", response_model=MonthlySeries, operation_id="getTemperature")
def temperature() -> MonthlySeries:
    """Sarajevo monthly mean temperature (Open-Meteo) — drives the heating profile."""
    try:
        return MonthlySeries(**svc.temperature_series())
    except FileNotFoundError as e:
        raise _missing(e) from None


@router.get("/solar/pv-yield", response_model=MonthlySeries, operation_id="getPvYield")
def pv_yield() -> MonthlySeries:
    """Solar output per installed kWp in Sarajevo, by month (PVGIS)."""
    try:
        return MonthlySeries(**svc.pv_yield_series())
    except FileNotFoundError as e:
        raise _missing(e) from None


@router.get("/club/baseline", response_model=Baseline, operation_id="getClubBaseline")
def club_baseline() -> Baseline:
    """Yearly electricity and travel: kWh, KM cost and t CO2 for the sample club."""
    return Baseline(**action_plan.baseline())


@router.get("/club/actions", response_model=ActionPlan, operation_id="getActionPlan")
def club_actions() -> ActionPlan:
    """Upgrades ranked by payback, with KM/CO2 saved and fee drop per child (summary bar)."""
    return ActionPlan(**action_plan.action_plan())


def _club(req: ClubRequest) -> dict | None:
    return req.club.model_dump() if req.club else None


@router.post("/club/baseline", response_model=Baseline, operation_id="calculateBaseline")
def calculate_baseline(req: ClubRequest) -> Baseline:
    """Baseline for the club in the body (`club: null` = sample club)."""
    return Baseline(**action_plan.baseline(_club(req)))


@router.post("/club/actions", response_model=ActionPlan, operation_id="calculateActionPlan")
def calculate_actions(req: ClubRequest) -> ActionPlan:
    """Ranked actions for the club in the body, optionally with a different electricity price."""
    return ActionPlan(**action_plan.action_plan(_club(req), req.electricity_price_km_per_kwh))


@router.post("/club/travel", response_model=SeasonTravel, operation_id="calculateSeasonTravel")
def season_travel(req: SeasonTravelRequest) -> SeasonTravel:
    """Season cost (KM) and CO2 of away travel: current mix vs cars, minibuses or a hired coach."""
    try:
        club = req.club.model_dump() if req.club else svc.sample_club()
        result = travel.season_travel(club, req.people_per_trip, req.share_with_partner)
    except FileNotFoundError as e:
        raise _missing(e) from None
    return SeasonTravel(**result)
