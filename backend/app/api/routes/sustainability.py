"""Topic 6 — The Sustainable Sports Club: energy, travel and equipment emissions."""

from fastapi import APIRouter, HTTPException, Query

from app.i18n import LangDep
from app.schemas import (
    AmountEstimate,
    ElectricityEstimate,
    ElectricityMix,
    EmissionFactor,
    IntensitySeries,
    TripComparison,
    TripRequest,
)
from app.services import emissions as svc

router = APIRouter(prefix="/sustainability", tags=["sustainability"])


def _not_found(e: KeyError) -> HTTPException:
    return HTTPException(404, str(e.args[0]) if e.args else "Not found")


@router.get(
    "/grid-intensity", response_model=list[IntensitySeries], operation_id="getGridIntensity"
)
def grid_intensity(
    countries: list[str] = Query(["BIH", "HRV", "SRB", "EU"]),
    from_year: int = Query(2010, ge=1990, le=2100),
) -> list[IntensitySeries]:
    try:
        return [IntensitySeries(**s) for s in svc.grid_series(countries, from_year)]
    except KeyError as e:
        raise _not_found(e) from None


@router.get("/electricity-mix", response_model=ElectricityMix, operation_id="getElectricityMix")
def electricity_mix(country: str = "BIH", year: int | None = None) -> ElectricityMix:
    try:
        return ElectricityMix(**svc.electricity_mix(country, year))
    except KeyError as e:
        raise _not_found(e) from None


@router.get("/electricity", response_model=ElectricityEstimate, operation_id="estimateElectricity")
def electricity(
    kwh: float = Query(gt=0, le=1e9), country: str = "BIH", year: int | None = None
) -> ElectricityEstimate:
    try:
        return ElectricityEstimate(**svc.electricity_emissions(kwh, country, year))
    except KeyError as e:
        raise _not_found(e) from None


@router.get("/factors", response_model=list[EmissionFactor], operation_id="listEmissionFactors")
def factors(category: str | None = None) -> list[EmissionFactor]:
    rows = svc.factor_table()
    if category:
        rows = rows[rows["category"] == category]
    return [EmissionFactor(**r) for r in rows.to_dict("records")]


@router.get("/estimate", response_model=AmountEstimate, operation_id="estimateAmount")
def estimate(key: str, amount: float = Query(gt=0, le=1e9)) -> AmountEstimate:
    try:
        return AmountEstimate(**svc.amount_emissions(key, amount))
    except KeyError as e:
        raise _not_found(e) from None


@router.post("/trip", response_model=TripComparison, operation_id="compareTrip")
def trip(req: TripRequest, lang: LangDep) -> TripComparison:
    try:
        return TripComparison(**svc.trip_options(**req.model_dump(), lang=lang))
    except KeyError as e:
        raise _not_found(e) from None
