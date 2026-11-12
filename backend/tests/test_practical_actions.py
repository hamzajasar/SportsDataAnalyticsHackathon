"""Upgrades scale with the club; free/low-cost actions; kit swap saves for families."""

import copy

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import actions

client = TestClient(app)


@pytest.fixture
def club():
    return {k: v for k, v in copy.deepcopy(actions.sample_club()).items() if k[0] != "_"}


def plan_for(club):
    r = client.post("/api/club/actions", json={"club": club})
    assert r.status_code == 200, r.text
    return {a["id"]: a for a in r.json()["actions"]}, r.json()


def test_sample_club_reference_costs_unchanged():
    by_id = {a["id"]: a for a in actions.rank_actions()["actions"]}
    assert by_id["led"]["cost_km"] == 9000
    assert by_id["solar"]["name"] == "Solar roof 20 kWp"
    assert by_id["insul"]["cost_km"] == 15000


def test_upgrades_scale_with_a_smaller_club(club):
    club["electricity_kwh_year"] = {"floodlights": 5500, "heating": 5000, "hall_and_other": 2500}
    by_id, _ = plan_for(club)
    assert by_id["led"]["cost_km"] == 2250  # 9,000 x 5,500 / 22,000
    assert by_id["insul"]["cost_km"] == 3750  # 15,000 x 5,000 / 20,000
    assert by_id["solar"]["name"] == "Solar roof 5 kWp"  # 20 x 13,000 / 52,000


def test_solar_size_limits(club):
    club["electricity_kwh_year"] = {"floodlights": 500000, "heating": 0, "hall_and_other": 0}
    assert plan_for(club)[0]["solar"]["name"] == "Solar roof 50 kWp"  # max
    club["electricity_kwh_year"] = {"floodlights": 0, "heating": 0, "hall_and_other": 0}
    solar = plan_for(club)[0]["solar"]
    assert solar["saves_km_year"] == 0 and solar["cost_km"] == 0


def test_free_and_low_cost_actions_present_and_first():
    p = actions.rank_actions()
    by_id = {a["id"]: a for a in p["actions"]}
    assert by_id["heat_setpoint"]["cost_type"] == "free"
    assert by_id["lights_off"]["cost_type"] == "low"
    assert by_id["led"]["cost_type"] == "investment"
    first_three = [a["cost_type"] for a in p["actions"][:3]]
    assert "investment" not in first_three  # cheapest wins first


def test_kit_swap_saves_for_families_not_the_club():
    p = actions.rank_actions()
    kit = next(a for a in p["actions"] if a["id"] == "kit_swap")
    assert kit["owner"] == "families" and not kit["counts_for_club"]
    assert kit["saves_km_year"] > 0 and kit["saves_kg_co2_year"] > 0
    assert p["families_save_km_year"] == kit["saves_km_year"]
    aff = client.post("/api/club/affordability", json={}).json()
    assert aff["families_save_per_child_km"] > 0
    assert "kit_swap" not in {a["id"] for a in aff["actions"]}
