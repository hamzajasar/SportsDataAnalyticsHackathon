import copy

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import actions

client = TestClient(app)


def afford(body=None):
    r = client.post("/api/club/affordability", json=body or {})
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture
def club():
    return {k: v for k, v in copy.deepcopy(actions.sample_club()).items() if k[0] != "_"}


def test_numbers_add_up():
    a = afford()
    assert sum(x["fee_drop_per_child_km"] for x in a["actions"]) == pytest.approx(
        a["total_fee_drop_per_child_km"], abs=0.5
    )
    assert a["cost_per_child_after_km"] == pytest.approx(
        a["cost_per_child_km"] - a["total_fee_drop_per_child_km"], abs=0.2
    )
    assert a["running_cost_km_year"] == a["electricity_km_year"] + a["travel_km_year"]


def test_consistent_with_action_plan_and_baseline():
    a = afford()
    plan = client.get("/api/club/actions").json()
    base = client.get("/api/club/baseline").json()
    assert a["total_fee_drop_per_child_km"] == pytest.approx(plan["fee_drop_per_child_km"], abs=0.1)
    assert a["electricity_km_year"] == pytest.approx(base["electricity_km"], abs=1)
    assert a["travel_km_year"] == base["travel_km_cost"]


def test_per_child_scales_with_children(club):
    one = afford({"club": club})
    club["children"] *= 2
    two = afford({"club": club})
    assert two["cost_per_child_km"] == pytest.approx(one["cost_per_child_km"] / 2, abs=0.1)
    assert two["illustrative_club"] is False and afford()["illustrative_club"] is True


def test_after_never_negative(club):
    club["travel"]["away_trips_per_team_year"] = 0
    club["electricity_kwh_year"] = {"floodlights": 100, "heating": 0, "hall_and_other": 0}
    assert afford({"club": club})["cost_per_child_after_km"] >= 0
