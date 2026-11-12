"""Affordability tab: running cost per child and how much each action lowers it."""

from fastapi import APIRouter

from app.i18n import LangDep
from app.schemas.affordability import Affordability
from app.schemas.club import ClubRequest
from app.services import affordability

router = APIRouter(tags=["club"])


@router.post(
    "/club/affordability", response_model=Affordability, operation_id="calculateAffordability"
)
def club_affordability(req: ClubRequest, lang: LangDep) -> Affordability:
    """Cost per child today, fee drop per action, cost per child after (`club: null` = sample)."""
    club = req.club.model_dump() if req.club else None
    return Affordability(
        **affordability.affordability(club, req.electricity_price_km_per_kwh, lang)
    )
