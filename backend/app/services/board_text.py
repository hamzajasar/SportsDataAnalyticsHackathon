"""Draft board decision in Bosnian, ready to print.

Deliberately a template, not generated text: every figure is inserted by code from the analysis, so
the document can never contain a number the model made up, it works offline, and it is testable.
Decimal comma and thousands dot, as is usual in Bosnian.
"""

from datetime import date

from app.i18n import M

MONTHS = [
    "januar", "februar", "mart", "april", "maj", "juni",
    "juli", "august", "septembar", "oktobar", "novembar", "decembar",
]  # fmt: skip
MONTHS_LOC = [  # "u ... "
    "januaru", "februaru", "martu", "aprilu", "maju", "junu",
    "julu", "augustu", "septembru", "oktobru", "novembru", "decembru",
]  # fmt: skip

ACTION_NAMES = {
    "carshare": "Zajednički prijevoz (popuniti minibus)",
    "led": "LED rasvjeta igrališta",
    "solar": "Solarni paneli na krovu",
    "insul": "Izolacija i toplotna pumpa",
}
CHECKS = {
    "floodlights": "tajmere reflektora i da li svjetla ostaju upaljena nakon treninga",
    "heating": "podešenu temperaturu grijanja i da li se griju neiskorištene prostorije ili sala",
    "baseload": "prethodni račun i stanje brojila, kako bi se isključila greška u obračunu",
}
PRICE_SOURCES = {
    "unit_price": "cijena po kWh štampana na računu",
    "total_per_kwh": "ukupan iznos računa podijeljen sa kWh, uključujući fiksne naknade",
    "assumed": "pretpostavljena cijena za BiH (Eurostat), jer račun ne sadrži cijenu",
    "fuel": "cijena struje nepromijenjena",
}
FUEL_NAMES = {"diesel": "dizel", "petrol": "benzin"}
SOURCES = (
    "Ember (emisije električne mreže), Eurostat (cijena struje), Open-Meteo (temperatura), "
    "PVGIS (solarni potencijal), UK GHG 2025 (faktori emisija vozila)."
)


def fmt(x: float, decimals: int = 0) -> str:
    """12002 -> '12.002'; 66.7 -> '66,7'."""
    s = f"{x:,.{decimals}f}"
    return s.replace(",", "\0").replace(".", ",").replace("\0", ".")


def _action_name(a: dict) -> str:
    """Always Bosnian, whatever language the plan was computed in."""
    if a["id"] in ACTION_NAMES:
        return ACTION_NAMES[a["id"]]
    key = f"action.{a['id']}"
    return M[key]["bs"] if key in M and "{" not in M[key]["bs"] else a["name"]


def _payback(a: dict) -> str:
    if a["payback_years"] is None:
        return "povrat nije moguće izračunati"
    if a["cost_km"] == 0:
        return "povrat odmah"
    return f"povrat za {fmt(a['payback_years'], 1)} god."


def _measures(top: list[dict]) -> list[str]:
    lines = ["3. Prijedlog mjera (rangirano po periodu povrata)"]
    for i, a in enumerate(top, 1):
        cost = "bez troška" if a["cost_km"] == 0 else f"trošak {fmt(a['cost_km'])} KM"
        lines.append(
            f"   {i}. {_action_name(a)}: {cost}, ušteda {fmt(a['saves_km_year'])} KM godišnje, "
            f"{_payback(a)}"
        )
    return lines


def _savings(plan: dict, club: dict) -> list[str]:
    after, before = plan["after"], plan["before"]
    lines = [
        f"   - Moguća ukupna ušteda: oko {fmt(after['total_saves_km_year'])} KM i "
        f"{fmt(after['total_saves_t_co2_year'], 1)} t CO₂ godišnje.",
        f"   - Članarina po djetetu mogla bi biti niža za oko "
        f"{fmt(after['fee_drop_per_child_km'], 1)} KM godišnje ({fmt(club['children'])} djece).",
    ]
    if round(before["total_saves_km_year"]) != round(after["total_saves_km_year"]):
        lines.append(
            f"   - Prije ovog računa procjena ušteda bila je "
            f"{fmt(before['total_saves_km_year'])} KM godišnje."
        )
    return lines


def _footer(analysis: dict, based_on: str) -> list[str]:
    lines = ["", "Napomene:", f"   - {based_on}", f"   - Izvori: {SOURCES}"]
    if analysis["illustrative_club"]:
        lines.append(
            "   - Podaci o klubu (broj djece, godišnja potrošnja, putovanja) su ILUSTRATIVNI "
            "i ne odgovaraju stvarnom klubu."
        )
    lines += ["", "Predsjednik Upravnog odbora: ______________________"]
    return lines


def _header(club: dict, analysis: dict, today: date) -> list[str]:
    lines = ["PRIJEDLOG ODLUKE UPRAVNOG ODBORA", club["name"], f"Datum: {today:%d.%m.%Y}.", ""]
    if analysis["illustrative_club"]:
        lines += [
            "NAPOMENA: Ovo je ILUSTRATIVNI primjer na podacima primjerka kluba, "
            "a ne stvarna odluka.",
            "",
        ]
    return lines


def _electricity_text(analysis: dict, club: dict, bill: dict, today: date) -> str:
    w, plan = analysis["waste"], analysis["plan"]
    m = bill["period_month"]
    year = f" {bill['period_year']}" if bill.get("period_year") else ""
    amount = f", iznos {fmt(bill['amount_km'], 2)} KM" if bill.get("amount_km") else ""
    pct = w["difference_pct"]
    temp_src = (
        "uobičajena za taj mjesec"
        if w.get("temperature_source_id", "typical") == "typical"
        else "stvarna temperatura mjeseca"
    )
    verdict = {
        "normal": "Potrošnja je u očekivanom rasponu (±10 %).",
        "above": (
            f"Potrošnja je {fmt(pct, 1)} % veća od očekivane (oko {fmt(w['excess_kwh'])} kWh, "
            f"odnosno {fmt(w['excess_km'])} KM viška u ovom mjesecu)."
        ),
        "high": (
            f"Potrošnja je znatno veća od očekivane: {fmt(pct or 0, 1)} % (oko "
            f"{fmt(w['excess_kwh'])} kWh, odnosno {fmt(w['excess_km'])} KM viška u ovom "
            "mjesecu). Potrebna je provjera."
        ),
        "below": f"Potrošnja je {fmt(abs(pct or 0), 1)} % manja od očekivane.",
        "unknown": "Očekivanu potrošnju nije moguće izračunati za ovaj klub.",
    }[w["status"]]

    lines = _header(club, analysis, today)
    lines += [
        f"Osnov: račun za električnu energiju za {MONTHS[m - 1]}{year}: potrošnja "
        f"{fmt(bill['kwh'])} kWh{amount}.",
        "",
        "1. Nalaz",
        f"   - Potrošnja u {MONTHS_LOC[m - 1]} iznosi {fmt(w['actual_kwh'])} kWh. Prema godišnjim "
        f"podacima kluba i temperaturi u Sarajevu ({fmt(w['temperature_c'], 1)} °C, {temp_src}) "
        f"očekuje se oko {fmt(w['expected_kwh'])} kWh.",
        f"   - {verdict}",
    ]
    if w["suggestions"]:
        lines.append("   - Prvo provjeriti:")
        lines += [f"       * {CHECKS[s]}" for s in w["suggestions"]]
    lines += [
        "",
        "2. Procjena na nivou godine",
        f"   - Na osnovu ovog računa godišnja potrošnja procjenjuje se na oko "
        f"{fmt(plan['annual_kwh_estimate'])} kWh (prije: "
        f"{fmt(plan['before']['electricity_kwh_year'])} kWh).",
        f"   - Cijena struje u proračunu: {fmt(plan['price_km_per_kwh_used'], 3)} KM/kWh "
        f"({PRICE_SOURCES[plan['price_source_id']]}).",
    ]
    lines += _savings(plan, club)
    lines += [""] + _measures(plan["after"]["top_actions"])
    top = plan["after"]["top_actions"][0]
    first = (
        "se u roku od 15 dana provjere navedene mogućnosti prekomjerne potrošnje i o nalazu "
        "izvijesti Upravni odbor;"
        if w["status"] in ("above", "high")
        else "se potrošnja električne energije i dalje prati svakog mjeseca;"
    )
    second = (
        f"se odmah uvede mjera „{_action_name(top)}”;"
        if top["cost_km"] == 0
        else f"se pristupi realizaciji mjere „{_action_name(top)}”: prikupiti najmanje dvije "
        "ponude do ____________;"
    )
    lines += [
        "",
        "4. Prijedlog odluke",
        "   Upravni odbor donosi odluku da:",
        f"   1. {first}",
        f"   2. {second}",
        "   3. se svaki mjesečni račun evidentira, a procjena ušteda ažurira.",
    ]
    return "\n".join(lines + _footer(analysis, _based_on_bs(analysis, bill)))


def _fuel_text(analysis: dict, club: dict, bill: dict, today: date) -> str:
    f, plan = analysis["fuel"], analysis["plan"]
    name = FUEL_NAMES.get(f["fuel_type"], f["fuel_type"])
    diff = f["difference_pct"]
    relation = (
        f"{fmt(abs(diff), 1)} % veća" if diff > 0 else f"{fmt(abs(diff), 1)} % manja"
    ) + " od naše pretpostavke"
    lines = _header(club, analysis, today)
    lines += [
        f"Osnov: račun za gorivo ({name}): {fmt(f['litres'], 1)} l, {fmt(f['amount_km'], 2)} KM.",
        "",
        "1. Nalaz",
        f"   - Cijena sa računa je {fmt(f['price_km_per_litre'], 2)} KM/l; to je {relation} "
        f"({fmt(f['assumed_km_per_litre'], 2)} KM/l).",
        "",
        "2. Posljedica na plan",
        f"   - Godišnji trošak goriva za gostovanja: "
        f"{fmt(plan['after']['travel_km_cost_year'])} KM "
        f"(prije: {fmt(plan['before']['travel_km_cost_year'])} KM).",
    ]
    lines += _savings(plan, club)
    lines += [""] + _measures(plan["after"]["top_actions"])
    lines += [
        "",
        "4. Prijedlog odluke",
        "   Upravni odbor donosi odluku da:",
        "   1. se računi za gorivo na gostovanjima evidentiraju i prilažu uz obračun "
        "putnih troškova;",
        "   2. se razmotri zajednički prijevoz sa partnerskim klubom radi smanjenja troškova;",
        "   3. se procjena ušteda ažurira nakon svakog novog računa.",
    ]
    return "\n".join(lines + _footer(analysis, _based_on_bs(analysis, bill)))


def decision_text_bs(analysis: dict, club: dict, bill: dict, today: date | None = None) -> str:
    today = today or date.today()
    if analysis["kind"] == "electricity":
        return _electricity_text(analysis, club, bill, today)
    return _fuel_text(analysis, club, bill, today)


def _based_on_bs(analysis: dict, bill: dict) -> str:
    if analysis["kind"] == "electricity":
        m = MONTHS[bill["period_month"] - 1]
        return (
            f"Procjena se zasniva na jednom računu ({m}) i godišnjim podacima kluba; godišnja "
            "potrošnja je preračunata iz ovog jednog mjeseca. Svaki dodatni račun čini je "
            "tačnijom."
        )
    name = FUEL_NAMES.get(bill.get("fuel_type"), "gorivo")
    return f"Procjena se zasniva na jednom računu za gorivo ({name}); cijena goriva je ažurirana."
