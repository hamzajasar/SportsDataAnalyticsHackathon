from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def quick(**answers):
    body = {"city": "Mostar", "children": 90, "teams": 3, **answers}
    r = client.post("/api/club/quick", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def test_cities_list():
    cities = client.get("/api/cities").json()
    assert len(cities) >= 30
    assert all(42 <= c["lat"] <= 46 and 15 <= c["lon"] <= 20 for c in cities)


def test_minimal_answers_give_a_usable_profile():
    r = quick()
    club = r["club"]
    assert club["lat"] == 43.3438 and club["heating_type"] == "unknown"
    assert {"location", "electricity_kwh_year", "avg_one_way_km"} <= set(r["estimated"])
    assert r["notes"]
    # the profile works with every club endpoint
    for path in ("baseline", "actions", "energy", "affordability", "travel"):
        assert client.post(f"/api/club/{path}", json={"club": club}).status_code == 200, path


def test_city_matching_ignores_accents_and_case():
    assert quick(city="bihac")["club"]["lat"] == quick(city="BIHAĆ")["club"]["lat"]
    assert (
        client.post(
            "/api/club/quick", json={"city": "Atlantis", "children": 5, "teams": 1}
        ).status_code
        == 422
    )


def test_bill_converts_to_kwh_and_overrides_estimate():
    r = quick(monthly_bill_km=291, heating_type="electric")  # 291 KM x 12 / 0.291 = 12,000 kWh
    kwh = r["club"]["electricity_kwh_year"]
    assert abs(sum(kwh.values()) - 12000) < 5
    assert kwh["heating"] > 0
    assert sum(quick(yearly_kwh=5000)["club"]["electricity_kwh_year"].values()) == 5000


def test_non_electric_heating_has_no_heating_kwh():
    assert quick(heating_type="district")["club"]["electricity_kwh_year"]["heating"] == 0


def test_transport_choice_sets_vehicles():
    assert quick(transport="cars")["club"]["travel"]["vehicles_per_trip"] == {
        "minibus": 0,
        "car": 6,
    }
    assert quick(transport="minibus")["club"]["travel"]["vehicles_per_trip"]["minibus"] == 2


def test_given_answers_are_not_marked_estimated():
    r = quick(away_games_per_team=10, avg_one_way_km=60, lat=43.35, lon=17.81)
    assert not {"location", "away_trips_per_team_year", "avg_one_way_km"} & set(r["estimated"])
    assert r["club"]["travel"]["avg_one_way_km"] == 60


def test_not_paying_electricity_is_carried_through():
    club = quick(pays_electricity=False)["club"]
    plan = client.post("/api/club/actions", json={"club": club}).json()
    assert any(a["owner"] == "facility_owner" for a in plan["actions"])
