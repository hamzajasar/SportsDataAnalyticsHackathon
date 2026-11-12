"""Season travel for a club: cost (KM) and CO2 (kg) of getting squads to away games.

Compares the club's current vehicle mix with all cars, minibuses only, and a hired coach,
for a whole season. Pure functions; every option carries the basis it was computed from.

  trips        = teams x away trips per team
  round trip   = 2 x average one-way km
  season cost  = trips x round trip x vehicles x cost per vehicle-km
  season CO2   = trips x round trip x vehicles x kg CO2e per vehicle-km

Fuel costs and the coach-hire price come from cost_assumptions.csv (the coach price is an
ASSUMPTION: there is no sourced figure yet). CO2 factors come from emissions.factor().
"""

import math

from app.services import club_data, emissions

CAR_OCCUPANCY = 3  # people per car in the "all cars" option (assumption, shown in UI)
MODES = ("car", "minibus", "coach")


def _costs() -> dict[str, float]:
    df = club_data.load_csv("costs")
    return dict(zip(df["key"], df["value"].astype(float), strict=True))


def _unit_rates() -> dict[str, dict]:
    """KM and kg CO2e per vehicle-km, with where each number comes from."""
    c = _costs()
    car = emissions.factor("car_average")
    van = emissions.factor("van_average")
    coach = emissions.factor("coach")
    return {
        "car": {"km": c["fuel_cost_car"], "co2": car["kg_co2e"], "label": "car"},
        "minibus": {"km": c["fuel_cost_minibus"], "co2": van["kg_co2e"], "label": "minibus"},
        "coach": {
            "km": c["coach_hire_km_per_km"],
            # UK factor is per passenger-km; a hired coach emits the same whatever it carries.
            "co2": coach["kg_co2e"] * emissions.COACH_AVG_OCCUPANCY,
            "label": "hired coach",
        },
    }


def _plural(n: int, word: str) -> str:
    plural = {"car": "cars", "minibus": "minibuses", "coach": "coaches"}[word]
    return f"{n} {word if n == 1 else plural}"


def season_travel(club: dict, people_per_trip: int = 18, share_with_partner: bool = False) -> dict:
    if people_per_trip < 1:
        raise ValueError("people_per_trip must be at least 1")
    t = club["travel"]
    trips = club["teams"] * t["away_trips_per_team_year"]
    round_trip_km = 2 * t["avg_one_way_km"]
    km_per_vehicle = trips * round_trip_km  # km driven by ONE vehicle used on every trip
    rates = _unit_rates()

    def option(mode: str, label: str, vehicles: dict[str, int], factor: float = 1.0) -> dict:
        cost = sum(n * km_per_vehicle * rates[v]["km"] for v, n in vehicles.items()) * factor
        co2 = sum(n * km_per_vehicle * rates[v]["co2"] for v, n in vehicles.items()) * factor
        return {
            "mode": mode,
            "label": label,
            "vehicles": vehicles,
            "cost_km": round(cost, 1),
            "co2_kg": round(co2, 1),
        }

    cars = math.ceil(people_per_trip / CAR_OCCUPANCY)
    minibuses = math.ceil(people_per_trip / emissions.VAN_SEATS)
    coaches = math.ceil(people_per_trip / emissions.COACH_SEATS)
    current = {v: n for v, n in t["vehicles_per_trip"].items() if v in MODES and n > 0}

    coach_label = f"{_plural(coaches, 'coach')} hired ({emissions.COACH_SEATS} seats)"
    if share_with_partner:
        coach_label += ", shared by two clubs"
    options = [
        option("current", "Current mix of vehicles", current),
        option("cars", f"{_plural(cars, 'car')} ({CAR_OCCUPANCY} per car)", {"car": cars}),
        option(
            "minibus",
            f"{_plural(minibuses, 'minibus')} ({emissions.VAN_SEATS} seats)",
            {"minibus": minibuses},
        ),
        option("coach", coach_label, {"coach": coaches}, 0.5 if share_with_partner else 1.0),
    ]
    base = options[0]
    for o in options:
        o["saving_vs_current_cost_km"] = round(base["cost_km"] - o["cost_km"], 1)
        o["saving_vs_current_co2_kg"] = round(base["co2_kg"] - o["co2_kg"], 1)
    options.sort(key=lambda o: o["cost_km"])

    shared_with: list[str] = []
    note = None
    if share_with_partner:
        partners = club_data.share_suggestions(club["lat"], club["lon"])["carpool_partners"]
        shared_with = [p["name"] for p in partners if p["name"]]
        if not shared_with:
            note = "No named partner club found nearby; a partner is assumed."
    return {
        "trips": trips,
        "round_trip_km": round_trip_km,
        "people_per_trip": people_per_trip,
        "share_with_partner": share_with_partner,
        "shared_with": shared_with,
        "note": note,
        "options": options,
        "cheapest": options[0]["mode"],
        "lowest_co2": min(options, key=lambda o: o["co2_kg"])["mode"],
        "assumptions": {
            "car_occupancy": CAR_OCCUPANCY,
            "minibus_seats": emissions.VAN_SEATS,
            "coach_seats": emissions.COACH_SEATS,
            "coach_avg_occupancy_for_co2": emissions.COACH_AVG_OCCUPANCY,
            "rates_per_vehicle_km": {
                m: {"cost_km": round(r["km"], 3), "kg_co2e": round(r["co2"], 4)}
                for m, r in rates.items()
            },
            "coach_hire_is_assumption": True,
        },
    }
