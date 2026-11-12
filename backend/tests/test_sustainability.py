"""Tests run against the committed reference tables (no downloads needed)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import emissions as svc

client = TestClient(app)


def test_grid_intensity_lookup_by_code_name_and_alias():
    bih = svc.grid_intensity("BIH", 2025)
    assert bih.entity == "Bosnia and Herzegovina"
    assert 300 < bih.gco2_per_kwh < 1000  # coal-heavy grid
    assert svc.grid_intensity("Bosnia and Herzegovina", 2025) == bih
    eu = svc.grid_intensity("EU", 2025)
    assert eu.gco2_per_kwh < bih.gco2_per_kwh


def test_grid_intensity_falls_back_to_latest_year():
    assert svc.grid_intensity("BIH", 2100).year <= 2100
    with pytest.raises(KeyError):
        svc.grid_intensity("BIH", 1800)
    with pytest.raises(KeyError):
        svc.grid_intensity("Atlantis")


def test_electricity_emissions_math():
    r = svc.electricity_emissions(1000, "BIH", 2025)
    assert r["kg_co2e"] == pytest.approx(r["gco2_per_kwh"], rel=1e-3)  # 1000 kWh * g/kWh / 1000


def test_trip_options_sorted_and_consistent():
    r = svc.trip_options(distance_km=100, people=18, round_trip=True, car_occupancy=3)
    kgs = [o["kg_co2e"] for o in r["options"]]
    assert kgs == sorted(kgs)
    cars = next(o for o in r["options"] if o["mode"] == "cars")
    assert cars["vehicles"] == 6
    car_factor = svc.factor("car_average")["kg_co2e"]
    assert cars["kg_co2e"] == pytest.approx(6 * 200 * car_factor, abs=0.1)
    assert r["options"][-1]["saving_vs_worst_kg"] == 0


def test_reused_kit_beats_new():
    new = svc.factor("material_clothing_new")["kg_co2e"]
    reused = svc.factor("material_clothing_reused")["kg_co2e"]
    assert new > 10 * reused


def test_every_factor_has_a_source():
    t = svc.factor_table()
    assert t["source"].notna().all() and (t["kg_co2e"] >= 0).all()


def test_api_endpoints():
    r = client.get("/api/sustainability/grid-intensity", params={"countries": ["BIH", "EU"]})
    assert r.status_code == 200 and len(r.json()) == 2
    r = client.get("/api/sustainability/electricity", params={"kwh": 5000})
    assert r.status_code == 200 and r.json()["kg_co2e"] > 0
    r = client.post("/api/sustainability/trip", json={"distance_km": 120, "people": 16})
    assert r.status_code == 200 and len(r.json()["options"]) == 4
    assert (
        client.get("/api/sustainability/estimate", params={"key": "nope", "amount": 1}).status_code
        == 404
    )
    assert (
        client.post("/api/sustainability/trip", json={"distance_km": -5, "people": 16}).status_code
        == 422
    )
    assert (
        client.get("/api/sustainability/electricity-mix").json()["entity"]
        == "Bosnia and Herzegovina"
    )
