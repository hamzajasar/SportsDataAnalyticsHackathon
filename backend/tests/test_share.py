from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
SARAJEVO = {"lat": 43.8563, "lon": 18.4131}


def test_nearest_sorted_and_filtered():
    r = client.get("/api/venues/nearest", params={**SARAJEVO, "n": 5, "leisure": "sports_hall"})
    v = r.json()
    assert r.status_code == 200 and 1 <= len(v) <= 5
    assert all(x["leisure"] == "sports_hall" for x in v)
    assert [x["distance_km"] for x in v] == sorted(x["distance_km"] for x in v)
    named = client.get("/api/venues/nearest", params={**SARAJEVO, "named_only": True}).json()
    assert all(x["name"] for x in named)


def test_distance_sarajevo_mostar():
    d = client.get(
        "/api/distance",
        params={"from_lat": 43.8563, "from_lon": 18.4131, "to_lat": 43.3438, "to_lon": 17.8078},
    ).json()
    assert 70 < d["straight_km"] < 80
    assert d["road_km_estimate"] > d["straight_km"]


def test_share_suggestions():
    s = client.get("/api/share/suggestions", params={**SARAJEVO, "radius_km": 5}).json()
    assert s["shared_pitch"] and s["carpool_partners"]
    assert all(v["distance_km"] <= 5 for v in s["shared_pitch"] + s["carpool_partners"])
    assert all(v["name"] for v in s["carpool_partners"])


def test_rejects_coordinates_outside_bih():
    assert client.get("/api/venues/nearest", params={"lat": 0, "lon": 0}).status_code == 422
    assert client.get("/api/distance", params={"from_lat": 43.8}).status_code == 422
