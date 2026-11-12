import pytest

from app.services import actions


def test_heating_profile_sums_to_annual():
    p = actions.heating_profile(20000)
    months = {m["month"]: m["heating_kwh"] for m in p["monthly"]}
    assert sum(months.values()) == pytest.approx(20000, abs=12)
    assert months[7] == 0 and months[1] > months[4]


def test_fit_heating_recovers_known_line():
    hdd = actions.heating_degree_days(actions.monthly_temps())
    fit = actions.fit_heating([500 + 12 * h for h in hdd])
    assert fit["r_squared"] == pytest.approx(1.0)
    assert fit["kwh_per_hdd"] == pytest.approx(12, abs=0.01)
    assert fit["baseload_kwh_per_month"] == pytest.approx(500, abs=0.5)


def test_rank_actions_sorted_and_consistent():
    r = actions.rank_actions()
    paybacks = [a["payback_years"] for a in r["actions"]]
    assert paybacks[0] == 0  # free car-sharing first
    assert paybacks == sorted(paybacks)
    assert r["total_saves_km_year"] == sum(a["saves_km_year"] for a in r["actions"])
    assert r["fee_drop_per_child_km"] == pytest.approx(
        r["total_saves_km_year"] / r["children"], abs=0.1
    )
    led = next(a for a in r["actions"] if a["id"] == "led")
    assert led["payback_years"] == pytest.approx(led["cost_km"] / led["saves_km_year"], abs=0.1)


def test_higher_price_shortens_payback():
    cheap = {a["id"]: a for a in actions.rank_actions(price_kwh=0.1)["actions"]}
    dear = {a["id"]: a for a in actions.rank_actions(price_kwh=0.4)["actions"]}
    assert dear["solar"]["payback_years"] < cheap["solar"]["payback_years"]


def test_baseline_bih_dirtier_than_croatia():
    bih = actions.baseline(country="BIH")["electricity_t_co2"]
    assert bih > actions.baseline(country="HRV")["electricity_t_co2"]
