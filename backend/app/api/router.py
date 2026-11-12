from fastapi import APIRouter

from app.api.routes import datasets, health, sample
from app.core.config import settings

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
if settings.datasets_enabled:
    api_router.include_router(datasets.router)
api_router.include_router(sample.router)
