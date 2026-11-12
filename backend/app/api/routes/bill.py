"""Check a bill: the club types in a bill's numbers, we analyse them."""

from fastapi import APIRouter, HTTPException

from app.i18n import LangDep
from app.schemas.bill import BillAnalyseRequest, BillAnalysis
from app.services import advisor

router = APIRouter(tags=["club"])


@router.post("/club/bill/analyse", response_model=BillAnalysis, operation_id="analyseBill")
def analyse_bill(req: BillAnalyseRequest, lang: LangDep) -> BillAnalysis:
    """Waste check, updated plan (before/after) and a draft board decision.

    Takes the numbers from the club's bill (no photo, no AI call). `club: null` = sample club.
    """
    club = req.club.model_dump() if req.club else None
    try:
        result = advisor.analyse_bill(club, req.bill.model_dump(), req.mean_temp_c, lang=lang)
    except advisor.BillInputError as e:
        raise HTTPException(422, str(e)) from None
    return BillAnalysis(**result)
