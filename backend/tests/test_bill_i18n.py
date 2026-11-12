"""Check a bill in English and Bosnian: no mixed languages in one response."""

import re

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
ELEC = {
    "kind": "electricity",
    "period_year": 2026,
    "period_month": 1,
    "kwh": 9420,
    "amount_km": 2900,
}
FUEL = {"kind": "fuel", "period_year": 2026, "period_month": 1, "litres": 120, "amount_km": 470,
        "fuel_type": "diesel"}  # fmt: skip
BS_MARK = re.compile(r"[čćšžđ]|\b(je|od|za|kluba|računa?|godišnj\w*|mjesec\w*)\b", re.IGNORECASE)
EN_MARK = re.compile(r"\b(the|and|of|is|per|bill|price|month|club|from|with|than)\b")
EN_ACTION_NAMES = ("Car-sharing", "Kit-swap", "Heat 1 °C", "Floodlights off", "LED floodlights")


def analyse(bill, lang):
    r = client.post("/api/club/bill/analyse", json={"bill": bill}, params={"lang": lang})
    assert r.status_code == 200, r.text
    return r.json()


def texts(d):
    """Every user-facing sentence in an analysis, except the always-Bosnian board text."""
    p = d["plan"]
    out = [p["price_source"], p["based_on"], *d["warnings"]]
    out += [a["name"] for side in ("before", "after") for a in p[side]["top_actions"]]
    if d["waste"]:
        out += [d["waste"]["temperature_source"], d["waste"]["basis"]]
    return out


def test_english_response_is_all_english():
    for bill in (ELEC, FUEL):
        d = analyse(bill, "en")
        assert not any(BS_MARK.search(s) for s in texts(d)), texts(d)
        assert d["board_text_lang"] == "en" and d["board_text"].startswith("DRAFT DECISION")
        assert not BS_MARK.search(d["board_text"].split("\n", 2)[2])  # skip the club name
        assert d["board_text_bs"].startswith("PRIJEDLOG ODLUKE")  # Bosnian copy still provided


def test_bosnian_response_is_all_bosnian():
    for bill in (ELEC, FUEL):
        d = analyse(bill, "bs")
        assert d["board_text_lang"] == "bs" and d["board_text"] == d["board_text_bs"]
        leftovers = [s for s in texts(d) if EN_MARK.search(s)]
        assert not leftovers, leftovers
        assert not any(name in d["board_text"] for name in EN_ACTION_NAMES)


def test_numbers_identical_in_both_languages():
    en, bs = analyse(ELEC, "en"), analyse(ELEC, "bs")
    assert en["waste"]["expected_kwh"] == bs["waste"]["expected_kwh"]
    assert en["plan"]["after"]["total_saves_km_year"] == bs["plan"]["after"]["total_saves_km_year"]
    assert en["waste"]["temperature_source_id"] == bs["waste"]["temperature_source_id"]


def test_bosnian_error_and_warning():
    r = client.post(
        "/api/club/bill/analyse", json={"bill": {"kind": "electricity"}}, params={"lang": "bs"}
    )
    assert r.status_code == 422 and "Za račun za struju" in r.text
    future = {**ELEC, "period_year": 2099}
    assert any("budućnosti" in w for w in analyse(future, "bs")["warnings"])
