"""Clubs on municipal facilities and with non-electric heating."""

import copy

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import actions

client = TestClient(app)


@pytest.fixture
def club():
    return {k: v for k, v in copy.deepcopy(actions.sample_club()).items() if k[0] != "_"}


def post(path, club):
    r = client.post(f"/api/club/{path}", json={"club": club})
    assert r.status_code == 200, r.text
    return r.json()


def test_defaults_keep_old_behaviour(club):
    plan = post("actions", club)
    for a in plan["actions"]:
        expected = "families" if a["id"] == "kit_swap" else "club"
        assert a["owner"] == expected and a["counts_for_club"] == (expected == "club")
    assert plan["facility_owner_saves_km_year"] == 0 and plan["notes"] == []


def test_club_not_paying_electricity(club):
    club["pays_electricity"] = False
    plan = post("actions", club)
    by_id = {a["id"]: a for a in plan["actions"]}
    for upgrade in ("led", "solar", "insul"):
        assert by_id[upgrade]["owner"] == "facility_owner"
        assert not by_id[upgrade]["counts_for_club"]
    assert by_id["carshare"]["counts_for_club"]
    # only travel counts for the club now
    assert plan["total_saves_km_year"] == by_id["carshare"]["saves_km_year"]
    assert plan["facility_owner_saves_km_year"] > 0
    assert any("doesn't pay the electricity" in n for n in plan["notes"])

    base = post("baseline", club)
    assert base["club_electricity_km"] == 0 and base["electricity_km"] > 0
    aff = post("affordability", club)
    assert aff["electricity_km_year"] == 0
    assert aff["running_cost_km_year"] == aff["travel_km_year"]
    assert {a["id"] for a in aff["actions"]} == {"carshare"}
    assert post("energy", club)["club_pays_electricity"] is False


def test_non_electric_heating_is_flagged(club):
    club["heating_type"] = "district"
    club["electricity_kwh_year"]["heating"] = 0
    plan = post("actions", club)
    assert any("Heating by district" in n for n in plan["notes"])
    insul = next(a for a in plan["actions"] if a["id"] == "insul")
    assert insul["saves_km_year"] == 0
    assert post("energy", club)["heating_type"] == "district"


def test_invalid_heating_type_rejected(club):
    club["heating_type"] = "nuclear"
    assert client.post("/api/club/actions", json={"club": club}).status_code == 422
