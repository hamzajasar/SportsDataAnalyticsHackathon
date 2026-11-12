"""Story-level check: a club volunteer's whole journey through the API.

Unit tests prove each endpoint on its own. This proves the story works end to end and that the
endpoints agree with each other: the same club produces the same electricity, travel cost and
savings wherever it shows up (Overview, Energy, Travel, Affordability, Check a bill).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ANSWERS = {
    "city": "Mostar",
    "children": 120,
    "teams": 5,
    "pays_electricity": True,
    "heating_type": "electric",
    "transport": "mixed",
}


def post(path: str, **body):
    r = client.post(f"/api/club/{path}", json=body)
    assert r.status_code == 200, f"{path}: {r.status_code} {r.text[:200]}"
    return r.json()


@pytest.fixture(scope="module")
def club() -> dict:
    # 1. the volunteer picks their city from the list, answers a few questions
    cities = [c["city"] for c in client.get("/api/cities").json()]
    assert ANSWERS["city"] in cities
    quick = post("quick", **ANSWERS)
    assert quick["club"]["children"] == 120 and quick["club"]["teams"] == 5
    assert quick["estimated"] and quick["notes"]  # everything guessed is reported back
    return quick["club"]


def test_one_club_gives_consistent_numbers_on_every_tab(club):
    baseline = post("baseline", club=club)
    plan = post("actions", club=club)
    energy = post("energy", club=club)
    travel = post("travel", club=club)
    afford = post("affordability", club=club)

    # Overview vs Energy: the same electricity, month by month and in total
    yearly_kwh = sum(club["electricity_kwh_year"].values())
    assert baseline["electricity_kwh"] == pytest.approx(yearly_kwh)
    assert energy["totals"]["total_kwh"] == pytest.approx(yearly_kwh, abs=15)
    assert len(energy["months"]) == 12

    # Overview vs Travel: today's mix costs what the baseline says
    current = next(o for o in travel["options"] if o["mode"] == "current")
    assert current["cost_km"] == pytest.approx(baseline["travel_km_cost"], abs=1)

    # Overview vs Affordability: the same savings, divided by the same children
    assert afford["children"] == club["children"] == plan["children"]
    assert afford["total_fee_drop_per_child_km"] == pytest.approx(
        plan["fee_drop_per_child_km"], abs=0.2
    )
    assert afford["running_cost_km_year"] == pytest.approx(
        afford["electricity_km_year"] + afford["travel_km_year"], abs=1
    )
    assert afford["cost_per_child_after_km"] <= afford["cost_per_child_km"]

    # the ranked actions are really ranked, and the headline is their sum
    paybacks = [a["payback_years"] for a in plan["actions"] if a["payback_years"] is not None]
    assert paybacks == sorted(paybacks)
    club_total = sum(a["saves_km_year"] for a in plan["actions"] if a["counts_for_club"])
    assert plan["total_saves_km_year"] == pytest.approx(club_total, abs=1)


def test_a_normal_bill_then_a_high_bill_tell_different_stories(club):
    expected = post("energy", club=club)["months"][0]["total_kwh"]  # January
    normal = post(
        "bill/analyse",
        club=club,
        bill={
            "kind": "electricity",
            "period_month": 1,
            "kwh": expected,
            "amount_km": expected * 0.3,
        },
    )
    high = post(
        "bill/analyse",
        club=club,
        bill={
            "kind": "electricity",
            "period_month": 1,
            "kwh": expected * 1.4,
            "amount_km": expected * 0.42,
        },
    )
    assert normal["waste"]["status"] == "normal" and not normal["waste"]["suggestions"]
    assert high["waste"]["status"] == "high" and high["waste"]["suggestions"]
    assert high["waste"]["excess_km"] > 0
    # a bigger bill means a bigger bill to save on: the plan reacts
    assert (
        high["plan"]["after"]["total_saves_km_year"]
        > normal["plan"]["after"]["total_saves_km_year"]
    )
    # both languages of the board text exist and carry the club's own name
    for key in ("board_text", "board_text_bs"):
        assert club["name"] in high[key], key
    assert high["illustrative_club"] is False


def test_the_sample_club_runs_the_same_journey():
    """`club: null` is the demo path judges see first: every endpoint must accept it."""
    for path in ("baseline", "actions", "energy", "travel", "affordability"):
        assert post(path, club=None)["illustrative_club"] is True, path
    bill = {"kind": "electricity", "period_month": 1, "kwh": 9420, "amount_km": 2900}
    assert post("bill/analyse", club=None, bill=bill)["waste"]["status"] == "high"


def test_sharing_a_coach_changes_the_travel_answer(club):
    alone = post("travel", club=club)
    shared = post("travel", club=club, share_with_partner=True)
    a = next(o for o in alone["options"] if o["mode"] == "coach")
    s = next(o for o in shared["options"] if o["mode"] == "coach")
    assert s["cost_km"] == pytest.approx(a["cost_km"] / 2, abs=0.2)
    assert shared["share_with_partner"] is True


def test_every_number_can_be_traced_to_a_source():
    """The Sources tab: every dataset has a credit line, so no number is unexplained."""
    sources = client.get("/api/sources").json()
    assert len(sources) >= 5 and all(s["credit"] and s["licence"] for s in sources)
    assert client.get("/api/health").json()["status"] == "ok"
