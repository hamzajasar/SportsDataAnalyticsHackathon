import copy

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import actions

client = TestClient(app)


def energy(body=None):
    r = client.post("/api/club/energy", json=body or {})
    assert r.status_code == 200, r.text
    return r.json()


def test_twelve_months_heating_follows_temperature():
    e = energy()
    m = e["months"]
    assert len(m) == 12
    assert m[0]["heating_kwh"] > m[6]["heating_kwh"]  # January > July
    assert e["illustrative_club"] is True


def test_monthly_use_adds_up_to_yearly_input():
    club = actions.sample_club()
    yearly = sum(club["electricity_kwh_year"].values())
    assert energy()["totals"]["total_kwh"] == pytest.approx(yearly, abs=12)  # rounding per month


def test_no_solar_by_default_and_cost_matches_baseline():
    e = energy()
    assert e["totals"]["solar_produced_kwh"] == 0
    assert e["totals"]["net_kwh"] == e["totals"]["total_kwh"]
    baseline = client.get("/api/club/baseline").json()
    assert e["totals"]["cost_km"] == pytest.approx(baseline["electricity_km"], abs=12)


def test_solar_reduces_net_but_never_below_zero():
    some = energy({"kwp": 20})
    assert 0 < some["totals"]["net_kwh"] < some["totals"]["total_kwh"]
    huge = energy({"kwp": 1000})
    assert all(m["net_kwh"] >= 0 for m in huge["months"])
    assert all(m["solar_used_kwh"] <= m["total_kwh"] for m in huge["months"])


def test_custom_club_and_validation():
    club = {k: v for k, v in copy.deepcopy(actions.sample_club()).items() if k[0] != "_"}
    club["electricity_kwh_year"] = {"floodlights": 1200, "heating": 0, "hall_and_other": 1200}
    e = energy({"club": club})
    assert e["illustrative_club"] is False
    assert all(m["heating_kwh"] == 0 and m["total_kwh"] == 200 for m in e["months"])
    assert client.post("/api/club/energy", json={"kwp": -1}).status_code == 422
