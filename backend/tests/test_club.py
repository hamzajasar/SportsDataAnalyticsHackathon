"""API over app/reference (committed, so these run in CI without downloads)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import club_data

client = TestClient(app)


def test_sample_club_and_assumptions():
    club = client.get("/api/club/sample").json()
    assert club["children"] > 0 and "electricity_kwh_year" in club
    a = client.get("/api/club/assumptions").json()
    assert {"costs", "upgrades", "pv_yield_monthly", "temperature_monthly"} <= a.keys()
    assert len(a["pv_yield_monthly"]) == 12 and len(a["temperature_monthly"]) == 12
    assert all(c["source"] for c in a["costs"])


def test_venues_filter_and_distance():
    all_v = client.get("/api/venues").json()
    assert len(all_v) > 3000
    halls = client.get("/api/venues", params={"leisure": "sports_hall"}).json()
    assert halls and all(v["leisure"] == "sports_hall" for v in halls)
    near = client.get(
        "/api/venues", params={"lat": 43.8563, "lon": 18.4131, "radius_km": 5, "limit": 20}
    ).json()
    dists = [v["distance_km"] for v in near]
    assert dists == sorted(dists) and all(d <= 5 for d in dists)


def test_venues_validation():
    assert client.get("/api/venues", params={"lat": 43.8}).status_code == 422
    assert client.get("/api/venues", params={"leisure": "../../etc"}).status_code == 422


def test_sources_have_credits():
    s = client.get("/api/sources").json()
    assert any(x["id"] == "osm" for x in s)


def test_only_whitelisted_files():
    with pytest.raises(KeyError):
        club_data.load_json("../../.env")
    with pytest.raises(KeyError):
        club_data.load_csv("../../.env")


def test_haversine_sarajevo_mostar():
    d = club_data._haversine_km(43.8563, 18.4131, 43.3438, 17.8078)
    assert 70 < d < 80


def test_temperature_and_pv_yield():
    t = client.get("/api/climate/temperature").json()
    assert len(t["months"]) == 12 and t["source"]
    winter, summer = t["months"][0]["value"], t["months"][6]["value"]
    assert winter < summer
    pv = client.get("/api/solar/pv-yield").json()
    assert len(pv["months"]) == 12
    assert 900 < pv["annual"] < 1500  # kWh/kWp/year, plausible for Sarajevo


def test_sample_club_is_typed_and_postable():
    club = client.get("/api/club/sample").json()
    assert "_note" not in club and "heating_note" not in club  # only profile fields
    # The sample can be sent straight back to the POST endpoints.
    r = client.post("/api/club/actions", json={"club": club})
    assert r.status_code == 200


def test_upgrades_are_typed():
    ups = client.get("/api/club/assumptions").json()["upgrades"]
    assert {u["id"] for u in ups} >= {"led", "solar", "insul", "carshare"}
    solar = next(u for u in ups if u["id"] == "solar")
    assert solar["kwp"] > 0 and solar["cost_km_per_kwp"] > 0
