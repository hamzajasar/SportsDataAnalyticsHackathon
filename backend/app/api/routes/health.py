from fastapi import APIRouter

from app.db.session import db_is_up
from app.schemas import Health

router = APIRouter(tags=["health"])


@router.get("/health", response_model=Health, operation_id="getHealth")
def health() -> Health:
    return Health(status="ok", database=db_is_up())
