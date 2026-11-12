import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def post(**body):
    r = client.post("/api/club/travel", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def by_mode(result):
    return {o["mode"]: o for o in result["options"]}


def test_current_mix_matches_baseline():
    """The season 'current mix' is the same club, so it must agree with /club/baseline."""
    base = client.get("/api/club/baseline").json()
    cur = by_mode(post())["current"]
    assert cur["cost_km"] == pytest.approx(base["travel_km_cost"], abs=0.5)
    assert cur["co2_kg"] / 1000 == pytest.approx(base["travel_t_co2"], abs=0.05)


def test_options_sorted_by_cost():
    r = post()
    costs = [o["cost_km"] for o in r["options"]]
    assert costs == sorted(costs)
    assert r["cheapest"] == r["options"][0]["mode"]
    assert {o["mode"] for o in r["options"]} == {"current", "cars", "minibus", "coach"}


def test_sharing_halves_the_coach_only():
    alone, shared = by_mode(post()), by_mode(post(share_with_partner=True))
    assert shared["coach"]["cost_km"] == pytest.approx(alone["coach"]["cost_km"] / 2, abs=0.1)
    assert shared["coach"]["co2_kg"] == pytest.approx(alone["coach"]["co2_kg"] / 2, abs=0.1)
    for mode in ("current", "cars", "minibus"):
        assert shared[mode] == alone[mode]


def test_partner_names_only_when_sharing():
    assert post()["shared_with"] == []
    shared = post(share_with_partner=True)
    assert shared["share_with_partner"] is True
    assert all(isinstance(n, str) and n for n in shared["shared_with"])
    assert shared["shared_with"] or shared["note"]  # either partners found, or told why not


def test_vehicle_counts_follow_people_per_trip():
    r = by_mode(post(people_per_trip=18))
    assert r["cars"]["vehicles"] == {"car": 6}  # 18 / 3
    assert r["minibus"]["vehicles"] == {"minibus": 3}  # 18 / 8, rounded up
    assert r["coach"]["vehicles"] == {"coach": 1}
    big = by_mode(post(people_per_trip=60))
    assert big["coach"]["vehicles"] == {"coach": 2}  # 50 seats each


def sample():
    return client.get("/api/club/sample").json()


def test_custom_club_changes_the_result():
    default = by_mode(post())["current"]["cost_km"]
    club = sample()
    club["travel"]["avg_one_way_km"] *= 2
    assert by_mode(post(club=club))["current"]["cost_km"] == pytest.approx(default * 2, abs=0.2)
    club = sample()
    club["teams"] //= 2  # 6 teams -> 3
    assert by_mode(post(club=club))["current"]["cost_km"] == pytest.approx(default / 2, abs=0.2)


def test_null_club_is_the_sample_club():
    assert post(club=None) == post()
    # Sending the sample's numbers explicitly gives the same result; only the label differs
    # (a club sent in the body counts as the user's own club).
    explicit, default = post(club=sample()), post()
    assert explicit.pop("illustrative_club") is False and default.pop("illustrative_club") is True
    assert explicit == default


def test_current_mix_uses_the_clubs_own_vehicles():
    club = sample()
    club["travel"]["vehicles_per_trip"] = {"minibus": 2, "car": 0}
    r = by_mode(post(club=club))
    assert r["current"]["vehicles"] == {"minibus": 2}


def bad_club(**changes):
    club = sample()
    club.update(changes)
    return club


@pytest.mark.parametrize(
    "body",
    [
        {"people_per_trip": 0},
        {"people_per_trip": 10_000},
        {"club": {"name": "incomplete"}},
        {"club": "not a club"},
    ],
)
def test_rejects_bad_input(body):
    assert client.post("/api/club/travel", json=body).status_code == 422


def test_rejects_invalid_club_values():
    for changes in ({"teams": 0}, {"lat": 0}, {"children": -1}):
        r = client.post("/api/club/travel", json={"club": bad_club(**changes)})
        assert r.status_code == 422, changes
