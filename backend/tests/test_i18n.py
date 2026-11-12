"""English / Bosnian: catalog completeness, language detection, formatting, endpoints."""

import string

import pytest
from fastapi.testclient import TestClient

from app.i18n import M, count, get_lang, num, pct
from app.main import app

client = TestClient(app)
BS = {"Accept-Language": "bs-BA,bs;q=0.9,en;q=0.5"}


def placeholders(s: str) -> set[str]:
    return {f for _, f, _, _ in string.Formatter().parse(s) if f}


@pytest.mark.parametrize("key", sorted(M))
def test_every_sentence_in_both_languages_with_same_placeholders(key):
    assert set(M[key]) == {"en", "bs"}
    assert all(M[key][lang].strip() for lang in ("en", "bs"))
    assert placeholders(M[key]["en"]) == placeholders(M[key]["bs"])


def test_language_detection():
    assert get_lang(None, None) == "en"
    assert get_lang("bs", "en-US") == "bs"  # ?lang= wins
    assert get_lang(None, "bs-BA,bs;q=0.9") == "bs"
    assert get_lang(None, "hr-HR") == "bs" and get_lang(None, "sr-Latn") == "bs"
    assert get_lang(None, "en-GB,bs;q=0.5") == "en"
    assert get_lang(None, "de-DE") == "en"


def test_number_formatting_and_counting():
    assert num(52000, "en") == "52,000" and num(52000, "bs") == "52.000"
    assert num(0.5, "bs", 1) == "0,5" and num(1234.5, "bs", 1) == "1.234,5"
    assert pct(0.4, "en") == "40%" and pct(0.4, "bs") == "40 %"
    assert count(1, "car", "bs") == "1 automobil" and count(3, "car", "bs") == "3 automobila"
    assert count(21, "car", "bs") == "21 automobil" and count(11, "car", "bs") == "11 automobila"
    assert count(1, "car", "en") == "1 car" and count(2, "coach", "en") == "2 coaches"


def test_action_plan_in_bosnian_same_numbers():
    en = client.get("/api/club/actions").json()
    bs = client.get("/api/club/actions", headers=BS).json()
    by_query = client.get("/api/club/actions", params={"lang": "bs"}).json()
    assert bs == by_query
    names = {a["id"]: a["name"] for a in bs["actions"]}
    assert names["led"] == "LED reflektori"
    assert names["carshare"].startswith("Zajednički prijevoz")
    # only words change, never numbers
    strip = lambda p: [(a["id"], a["saves_km_year"], a["payback_years"]) for a in p["actions"]]  # noqa: E731
    assert strip(en) == strip(bs)
    assert en["total_saves_km_year"] == bs["total_saves_km_year"]


@pytest.mark.parametrize(
    "path,body,check",
    [
        ("/api/club/affordability", {}, lambda r: r["scope"].startswith("Samo struja")),
        ("/api/club/energy", {}, lambda r: r["method"][1].startswith("Reflektori")),
        ("/api/club/travel", {}, lambda r: any("kombinacija" in o["label"] for o in r["options"])),
        (
            "/api/club/quick",
            {"city": "Mostar", "children": 50, "teams": 2},
            lambda r: r["club"]["name"] == "Moj klub" and r["notes"][0].startswith("Lokacija"),
        ),
        (
            "/api/sustainability/trip",
            {"distance_km": 100, "people": 18},
            lambda r: any(o["label"] == "Voz (redovna linija)" for o in r["options"]),
        ),
    ],
)
def test_post_endpoints_answer_in_bosnian(path, body, check):
    r = client.post(path, json=body, headers=BS)
    assert r.status_code == 200, r.text
    assert check(r.json())


def test_get_endpoints_answer_in_bosnian():
    share = client.get("/api/share/suggestions", params={"lat": 43.85, "lon": 18.41}, headers=BS)
    assert share.json()["note"].startswith("Partneri")
    dist = client.get(
        "/api/distance",
        params={"from_lat": 43.85, "from_lon": 18.41, "to_lat": 43.34, "to_lon": 17.81},
        headers=BS,
    )
    assert "zračnom linijom" in dist.json()["note"]


def test_bosnian_error_message():
    r = client.post(
        "/api/club/quick", json={"city": "Atlantis", "children": 5, "teams": 1}, headers=BS
    )
    assert r.status_code == 422 and "Nepoznat grad" in r.text
