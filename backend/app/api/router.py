from fastapi import APIRouter

from app.api.routes import (
    affordability,
    bill,
    club,
    energy,
    health,
    quick,
    share,
    sustainability,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(sustainability.router)
api_router.include_router(club.router)
api_router.include_router(bill.router)
api_router.include_router(energy.router)
api_router.include_router(affordability.router)
api_router.include_router(quick.router)
api_router.include_router(share.router)
