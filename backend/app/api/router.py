from fastapi import APIRouter

from app.api.routes import (
    affordability,
    bill,
    club,
    datasets,
    energy,
    health,
    quick,
    share,
    sustainability,
)
from app.core.config import settings

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
if settings.datasets_enabled:
    api_router.include_router(datasets.router)
api_router.include_router(sustainability.router)
api_router.include_router(club.router)
api_router.include_router(bill.router)
api_router.include_router(energy.router)
api_router.include_router(affordability.router)
api_router.include_router(quick.router)
api_router.include_router(share.router)
