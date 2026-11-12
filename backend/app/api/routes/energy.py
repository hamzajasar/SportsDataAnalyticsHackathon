"""Energy tab: the club's electricity month by month, with optional solar."""

from fastapi import APIRouter

from app.schemas.energy import EnergyProfile, EnergyRequest
from app.services import energy

router = APIRouter(tags=["club"])


@router.post("/club/energy", response_model=EnergyProfile, operation_id="calculateEnergyProfile")
def club_energy(req: EnergyRequest) -> EnergyProfile:
    """12 months of use, solar, net kWh, cost and CO2 for the club (`club: null` = sample)."""
    club = req.club.model_dump() if req.club else None
    return EnergyProfile(**energy.energy_profile(club, req.kwp, req.electricity_price_km_per_kwh))
