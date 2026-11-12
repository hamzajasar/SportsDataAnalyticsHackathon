"""Distances, nearest venues and sharing suggestions (car-pool, shared pitches) — OSM venues."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.i18n import LangDep
from app.schemas import Distance, ShareSuggestions, Venue
from app.services import club_data as svc

router = APIRouter(tags=["share"])

# BiH bounding box (rough) — rejects swapped/invalid coordinates early.
# Annotated types (not shared Query objects) so each parameter keeps its own name.
Lat = Annotated[float, Query(ge=42, le=46)]
Lon = Annotated[float, Query(ge=15, le=20)]
LEISURE = "^(pitch|stadium|sports_centre|sports_hall)$"


@router.get("/venues/nearest", response_model=list[Venue], operation_id="nearestVenues")
def nearest(
    lat: Lat,
    lon: Lon,
    n: Annotated[int, Query(ge=1, le=100)] = 10,
    leisure: Annotated[str | None, Query(pattern=LEISURE)] = None,
    named_only: bool = False,
) -> list[Venue]:
    try:
        return [Venue(**v) for v in svc.nearest(lat, lon, n, leisure, named_only)]
    except FileNotFoundError as e:
        raise HTTPException(503, str(e)) from None


@router.get("/distance", response_model=Distance, operation_id="getDistance")
def distance(from_lat: Lat, from_lon: Lon, to_lat: Lat, to_lon: Lon, lang: LangDep) -> Distance:
    return Distance(**svc.distance(from_lat, from_lon, to_lat, to_lon, lang))


@router.get("/share/suggestions", response_model=ShareSuggestions, operation_id="shareSuggestions")
def share(
    lat: Lat,
    lon: Lon,
    lang: LangDep,
    radius_km: Annotated[float, Query(gt=0, le=100)] = 10,
    n: Annotated[int, Query(ge=1, le=50)] = 5,
) -> ShareSuggestions:
    try:
        return ShareSuggestions(**svc.share_suggestions(lat, lon, radius_km, n, lang))
    except FileNotFoundError as e:
        raise HTTPException(503, str(e)) from None
