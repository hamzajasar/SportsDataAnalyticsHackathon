from fastapi import APIRouter

from app.schemas import SampleStats
from app.services.sample import sample_stats

router = APIRouter(prefix="/sample", tags=["sample"])


@router.get("/stats", response_model=SampleStats, operation_id="getSampleStats")
def get_sample_stats() -> SampleStats:
    return sample_stats()
