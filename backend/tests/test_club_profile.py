"""POST /api/club/baseline and /api/club/actions with a club profile in the body."""

import copy

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import actions

client = TestClient(app)


@pytest.fixture
def club():
    c = copy.deepcopy(actions.sample_club())
    return {k: v for k, v in c.items() if not k.startswith("_") and k != "heating_note"}


def post_actions(body):
    r = client.post("/api/club/actions", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def test_empty_body_equals_sample_get():
    assert (
        client.post("/api/club/baseline", json={}).json() == client.get("/api/club/baseline").json()
    )
    assert post_actions({}) == client.get("/api/club/actions").json()


def test_sample_is_illustrative_custom_club_is_not(club):
    assert post_actions({})["assumptions"]["illustrative_club"] is True
    assert post_actions({"club": club})["assumptions"]["illustrative_club"] is False


def test_doubling_children_halves_fee_drop(club):
    base = post_actions({"club": club})
    club["children"] *= 2
    doubled = post_actions({"club": club})
    assert doubled["total_saves_km_year"] == base["total_saves_km_year"]
    assert doubled["fee_drop_per_child_km"] == pytest.approx(
        base["fee_drop_per_child_km"] / 2, abs=0.1
    )


def test_no_floodlights_means_led_saves_nothing(club):
    club["electricity_kwh_year"]["floodlights"] = 0
    led = next(a for a in post_actions({"club": club})["actions"] if a["id"] == "led")
    assert led["saves_km_year"] == 0 and led["saves_kwh_year"] == 0


def test_club_numbers_flow_into_baseline(club):
    club["electricity_kwh_year"] = {"floodlights": 1000, "heating": 2000, "hall_and_other": 3000}
    b = client.post("/api/club/baseline", json={"club": club}).json()
    assert b["electricity_kwh"] == 6000


def test_price_override_changes_savings(club):
    cheap = post_actions({"club": club, "electricity_price_km_per_kwh": 0.1})
    dear = post_actions({"club": club, "electricity_price_km_per_kwh": 0.5})
    assert dear["total_saves_km_year"] > cheap["total_saves_km_year"]
    assert dear["assumptions"]["electricity_price_km_per_kwh"] == 0.5


def test_invalid_club_rejected(club):
    club["children"] = 0
    assert client.post("/api/club/actions", json={"club": club}).status_code == 422
    assert (
        client.post("/api/club/actions", json={"electricity_price_km_per_kwh": -1}).status_code
        == 422
    )
