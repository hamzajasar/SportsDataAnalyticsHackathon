"""API over data/clean (committed, so these run in CI without downloads)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import club_data

client = TestClient(app)


def test_sample_club_and_assumptions():
    club = client.get("/api/club/sample").json()
    assert club["children"] > 0 and "electricity_kwh_year" in club
    a = client.get("/api/club/assumptions").json()
    assert {"prices", "upgrades", "pv_yield", "monthly_temp"} <= a.keys()


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
        club_data.load("../../.env")


def test_haversine_sarajevo_mostar():
    d = club_data._haversine_km(43.8563, 18.4131, 43.3438, 17.8078)
    assert 70 < d < 80
