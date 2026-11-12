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


def test_endpoints_serve_the_live_model():
    from app.services import actions

    p = client.get("/api/club/actions").json()
    live = actions.rank_actions()
    assert p["example"] is False
    assert p["total_saves_km_year"] == live["total_saves_km_year"]
    assert [a["id"] for a in p["actions"]] == [a["id"] for a in live["actions"]]
    assert client.get("/api/club/baseline").json()["example"] is False
