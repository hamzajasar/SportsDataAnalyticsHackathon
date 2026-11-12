"""Check a bill: sanity checks, waste detector, plan update, Bosnian board text."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.bill import BillReading
from app.services import bill_checks, board_text, waste

client = TestClient(app)


def reading(**kw) -> BillReading:
    base = dict(
        kind="electricity", period_year=2026, period_month=1, kwh_total=6600.0,
        amount_total_km=1980.0, confidence="high",
    )  # fmt: skip
    return BillReading(**{**base, **kw})


def test_plausibility_flags_wrong_numbers():
    today = date(2026, 11, 12)
    assert bill_checks.plausibility_warnings(reading(), today) == []
    w = bill_checks.plausibility_warnings(reading(period_year=2027, period_month=3), today)
    assert any("future" in x for x in w)
    w = bill_checks.plausibility_warnings(reading(kwh_total=900_000.0), today)
    assert any("implausible" in x for x in w)
    w = bill_checks.plausibility_warnings(reading(kind="other", unreadable_reason="blurry"), today)
    assert w == ["blurry"]
    w = bill_checks.plausibility_warnings(reading(period_year=None, period_month=None), today)
    assert w == []  # an unknown period must not crash the check
    w = bill_checks.plausibility_warnings(
        reading(kind="fuel", litres=40.0, amount_total_km=20.0, fuel_type="diesel"), today
    )
    assert any("per litre" in x for x in w)


# ---- waste detector -----------------------------------------------------------------------


def club() -> dict:
    return client.get("/api/club/sample").json()


def test_expected_month_matches_the_energy_tab():
    energy = client.post("/api/club/energy", json={}).json()["months"]
    for m in (1, 4, 7, 12):
        exp = waste.expected_month_kwh(club(), m)["total"]
        assert exp == pytest.approx(energy[m - 1]["total_kwh"], abs=1)


@pytest.mark.parametrize(
    ("kwh", "status"),
    [(7188, "normal"), (7900, "normal"), (8200, "above"), (9420, "high"), (6000, "below")],
)
def test_waste_status_bands(kwh, status):
    assert waste.check_month(club(), 1, kwh, 0.3)["status"] == status


def test_headline_example_is_31_percent_above():
    w = waste.check_month(club(), 1, 9420, 0.3)
    assert w["difference_pct"] == pytest.approx(31.0, abs=0.1)
    assert w["excess_kwh"] == 2232
    assert w["excess_km"] == pytest.approx(2232 * 0.3, abs=1)
    assert set(w["suggestions"]) == {"floodlights", "heating", "baseload"}


def test_real_temperature_changes_what_the_weather_explains():
    typical = waste.check_month(club(), 1, 9420, 0.3)
    cold = waste.check_month(club(), 1, 9420, 0.3, mean_temp_c=-6)
    assert cold["expected_kwh"] > typical["expected_kwh"]
    assert cold["status"] == "normal" and typical["status"] == "high"


def test_summer_flag_does_not_blame_heating():
    w = waste.check_month(club(), 7, 6000, 0.3)  # July expected is ~2.7 MWh
    assert w["status"] == "high" and "heating" not in w["suggestions"]


# ---- analysis -----------------------------------------------------------------------------


def analyse(bill: dict, **kw):
    r = client.post("/api/club/bill/analyse", json={"bill": bill, **kw})
    return r


ELEC = {
    "kind": "electricity",
    "period_year": 2026,
    "period_month": 1,
    "kwh": 9420,
    "amount_km": 2900,
}


def test_high_bill_raises_the_plan_and_says_how_thin_the_evidence_is():
    d = analyse(ELEC).json()
    assert d["kind"] == "electricity" and d["illustrative_club"] is True
    assert d["waste"]["status"] == "high"
    plan = d["plan"]
    assert plan["after"]["electricity_kwh_year"] > plan["before"]["electricity_kwh_year"]
    assert plan["after"]["fee_drop_per_child_km"] > plan["before"]["fee_drop_per_child_km"]
    assert plan["scale_factor"] == pytest.approx(
        9420 / waste.expected_month_kwh(club(), 1)["total"], abs=0.01
    )
    assert "One bill" in plan["based_on"]


def test_price_comes_from_the_bill_in_order_of_trust():
    printed = analyse({**ELEC, "unit_price_km_per_kwh": 0.21}).json()["plan"]
    assert printed["price_source_id"] == "unit_price" and printed["price_km_per_kwh_used"] == 0.21
    total = analyse(ELEC).json()["plan"]
    assert total["price_source_id"] == "total_per_kwh"
    assert total["price_km_per_kwh_used"] == pytest.approx(2900 / 9420, abs=1e-3)
    assumed = analyse({k: v for k, v in ELEC.items() if k != "amount_km"}).json()["plan"]
    assert assumed["price_source_id"] == "assumed"


def test_one_absurd_bill_cannot_move_the_year_more_than_4x():
    d = analyse({**ELEC, "kwh": 900_000}).json()
    assert d["plan"]["scale_factor"] == 4.0
    assert any("limited" in w for w in d["warnings"])


def test_a_below_expected_bill_lowers_the_savings():
    d = analyse({**ELEC, "kwh": 5000, "amount_km": 1500}).json()
    assert d["waste"]["status"] == "below" and d["waste"]["suggestions"] == []
    assert d["plan"]["after"]["total_saves_km_year"] < d["plan"]["before"]["total_saves_km_year"]


def test_fuel_receipt_updates_travel_cost():
    fuel = {"kind": "fuel", "fuel_type": "diesel", "litres": 40, "amount_km": 160}
    d = analyse(fuel).json()
    assert d["waste"] is None and d["fuel"]["price_km_per_litre"] == 4.0
    assert d["fuel"]["difference_pct"] == pytest.approx((4.0 / 3.79 - 1) * 100, abs=0.1)
    assert d["plan"]["after"]["travel_km_cost_year"] > d["plan"]["before"]["travel_km_cost_year"]
    assert d["plan"]["after"]["electricity_kwh_year"] == d["plan"]["before"]["electricity_kwh_year"]
    petrol = analyse({**fuel, "fuel_type": "petrol", "amount_km": 100}).json()
    assert (
        petrol["plan"]["after"]["travel_km_cost_year"]
        < petrol["plan"]["before"]["travel_km_cost_year"]
    )


@pytest.mark.parametrize(
    "bill",
    [
        {"kind": "electricity", "kwh": 5000},  # no month
        {"kind": "electricity", "period_month": 1},  # no kWh
        {"kind": "electricity", "kwh": -5, "period_month": 1},
        {"kind": "electricity", "kwh": 5000, "period_month": 13},
        {"kind": "fuel", "litres": 40},
        {"kind": "fuel", "litres": 40, "amount_km": 160, "fuel_type": "lpg"},
        {"kind": "other"},
    ],
)
def test_analysis_rejects_incomplete_or_invalid_bills(bill):
    assert analyse(bill).status_code == 422


def test_a_custom_club_is_not_labelled_illustrative():
    mine = {**club(), "name": "NK Test Mostar", "children": 90}
    d = analyse(ELEC, club=mine).json()
    assert d["illustrative_club"] is False
    assert "NK Test Mostar" in d["board_text_bs"] and "ILUSTRATIVN" not in d["board_text_bs"]


# ---- Bosnian board text -------------------------------------------------------------------


def test_number_format_is_bosnian():
    assert board_text.fmt(12002) == "12.002"
    assert board_text.fmt(66.7, 1) == "66,7"
    assert board_text.fmt(1234567.891, 2) == "1.234.567,89"
    assert board_text.fmt(0, 1) == "0,0"


def test_board_text_carries_the_figures_and_the_decision():
    d = analyse(ELEC).json()
    text = d["board_text_bs"]
    plan, w = d["plan"], d["waste"]
    for needle in (
        "PRIJEDLOG ODLUKE UPRAVNOG ODBORA",
        "januar 2026",
        "u januaru",
        "9.420 kWh",
        "31,0 %",
        board_text.fmt(w["excess_km"]) + " KM",
        board_text.fmt(plan["after"]["total_saves_km_year"]) + " KM",
        board_text.fmt(plan["after"]["fee_drop_per_child_km"], 1) + " KM",
        "Upravni odbor donosi odluku",
        "ILUSTRATIVN",
        "Predsjednik Upravnog odbora",
    ):
        assert needle in text, needle
    assert "reflektora" in text  # the first thing to check
    assert not any(bad in text for bad in ("None", "nan", "{", "}"))


def test_board_text_changes_with_the_finding():
    normal = analyse({**ELEC, "kwh": 7200, "amount_km": 2100}).json()["board_text_bs"]
    assert "u očekivanom rasponu" in normal and "Prvo provjeriti" not in normal
    assert "se potrošnja električne energije i dalje prati" in normal
    high = analyse(ELEC).json()["board_text_bs"]
    assert "Potrebna je provjera" in high and "u roku od 15 dana" in high


def test_fuel_board_text():
    text = analyse({"kind": "fuel", "fuel_type": "diesel", "litres": 40, "amount_km": 160}).json()[
        "board_text_bs"
    ]
    assert "račun za gorivo (dizel)" in text and "4,00 KM/l" in text
    assert "se računi za gorivo" in text


def test_every_month_has_a_name_in_both_cases():
    assert len(board_text.MONTHS) == len(board_text.MONTHS_LOC) == 12
    for m in range(1, 13):
        d = analyse({**ELEC, "period_month": m}).json()
        assert board_text.MONTHS[m - 1] in d["board_text_bs"]
