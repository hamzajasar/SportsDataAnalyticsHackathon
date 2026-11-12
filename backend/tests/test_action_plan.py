from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_action_plan_shape_and_consistency():
    p = client.get("/api/club/actions").json()
    acts = p["actions"]
    assert acts and p["children"] > 0
    paybacks = [a["payback_years"] for a in acts if a["payback_years"] is not None]
    assert paybacks == sorted(paybacks)  # ranked by payback
    assert p["total_saves_km_year"] == sum(a["saves_km_year"] for a in acts)
    assert abs(p["fee_drop_per_child_km"] - p["total_saves_km_year"] / p["children"]) < 0.1
    assert "example" in p


def test_baseline():
    b = client.get("/api/club/baseline").json()
    assert b["electricity_kwh"] > 0 and b["travel_t_co2"] > 0 and "example" in b
