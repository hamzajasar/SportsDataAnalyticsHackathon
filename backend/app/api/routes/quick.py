"""Quick start: easy questions in, full club profile out (+ BiH city list)."""

from fastapi import APIRouter, HTTPException

from app.schemas.quick import City, QuickClubInput, QuickClubResult
from app.services import quick_start

router = APIRouter(tags=["club"])


@router.get("/cities", response_model=list[City], operation_id="listCities")
def list_cities() -> list[City]:
    """BiH cities with approximate centre coordinates, for the club's location picker."""
    return [City(**c) for c in quick_start.cities()]


@router.post("/club/quick", response_model=QuickClubResult, operation_id="quickClub")
def quick_club(answers: QuickClubInput) -> QuickClubResult:
    """Turn a few easy answers into a full club profile, marking every estimated value."""
    if answers.city and (answers.lat is None) != (answers.lon is None):
        raise HTTPException(422, "Give both lat and lon, or neither")
    try:
        return QuickClubResult(**quick_start.quick_club(answers.model_dump()))
    except KeyError as e:
        raise HTTPException(422, str(e.args[0])) from None
