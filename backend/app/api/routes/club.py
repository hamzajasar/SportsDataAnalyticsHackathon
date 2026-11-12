"""Club data, assumptions, venues and sources (from data/clean, shared via git)."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.schemas import ClubAssumptions, Source, Venue
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
