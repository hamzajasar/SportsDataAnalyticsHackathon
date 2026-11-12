"""'Snap your bill': read a photo with AI, then analyse the numbers a person confirmed."""

from fastapi import APIRouter, HTTPException, Request, UploadFile

from app.core.config import settings
from app.schemas.bill import BillAnalyseRequest, BillAnalysis, BillReadResponse
from app.services import advisor, bill_reader
from app.services.ratelimit import RateLimiter

router = APIRouter(tags=["club"])
limiter = RateLimiter(lambda: settings.bill_reads_per_hour)


@router.post("/club/bill/read", response_model=BillReadResponse, operation_id="readBill")
def read_bill(request: Request, file: UploadFile) -> BillReadResponse:
    """Read an electricity bill or fuel receipt photo (JPEG, PNG, WebP or GIF, up to 5 MB).

    The photo is processed in memory and not stored. The numbers are a first reading: show them to
    the user to confirm or correct before calling `/club/bill/analyse`.
    """
    key = request.client.host if request.client else "unknown"
    if not limiter.allow(key):
        raise HTTPException(
            429,
            "Too many bill readings from this address; try again later.",
            headers={"Retry-After": str(limiter.retry_after(key))},
        )
    image = file.file.read(bill_reader.MAX_IMAGE_BYTES + 1)  # one byte over the cap is enough
    try:
        reading = bill_reader.read_bill(image)
    except bill_reader.BillReaderError as e:
        raise HTTPException(e.status_code, str(e)) from None
    return BillReadResponse(
        reading=reading,
        warnings=bill_reader.plausibility_warnings(reading),
        model=settings.anthropic_model,
    )


@router.post("/club/bill/analyse", response_model=BillAnalysis, operation_id="analyseBill")
def analyse_bill(req: BillAnalyseRequest) -> BillAnalysis:
    """Waste check, updated plan (before/after) and a draft board decision in Bosnian.

    Takes the confirmed numbers, not a photo, and makes no AI call. `club: null` = sample club.
    """
    club = req.club.model_dump() if req.club else None
    try:
        result = advisor.analyse_bill(club, req.bill.model_dump(), req.mean_temp_c)
    except advisor.BillInputError as e:
        raise HTTPException(422, str(e)) from None
    return BillAnalysis(**result)
