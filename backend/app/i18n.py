"""English / Bosnian for every sentence the API sends to users.

Language comes from `?lang=bs|en` or the `Accept-Language` header (bs, hr, sr → Bosnian);
default English. Add a sentence: one key with BOTH languages and the same {placeholders}
(tests/test_i18n.py checks this). Numbers go in pre-formatted with num()/pct().
"""

from typing import Annotated, Literal

from fastapi import Depends, Header, Query

Lang = Literal["en", "bs"]
SOUTH_SLAVIC = ("bs", "hr", "sr", "sh", "cnr")


def get_lang(
    lang: Annotated[Lang | None, Query(description="Response language: en or bs")] = None,
    accept_language: Annotated[str | None, Header()] = None,
) -> Lang:
    """FastAPI dependency: ?lang= wins, then Accept-Language, else English."""
    if lang:
        return lang
    for part in (accept_language or "").split(","):
        tag = part.split(";")[0].strip().lower()
        if tag.startswith(SOUTH_SLAVIC):
            return "bs"
        if tag.startswith("en"):
            return "en"
    return "en"


LangDep = Annotated[Lang, Depends(get_lang)]  # add `lang: LangDep` to a route


def num(x: float, lang: Lang, decimals: int = 0) -> str:
    """52000 -> '52,000' (en) / '52.000' (bs); 0.5 -> '0.5' / '0,5'."""
    s = f"{x:,.{decimals}f}"
    if lang == "bs":
        s = s.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")
    return s


def pct(share: float, lang: Lang) -> str:
    """0.4 -> '40%' (en) / '40 %' (bs)."""
    return f"{share * 100:.0f}%" if lang == "en" else f"{share * 100:.0f} %"


def plural(n: int, lang: Lang, one: str, many: str, bs_one: str, bs_many: str) -> str:
    """Count + noun. Bosnian: 1/21/31… take the singular, everything else the genitive
    (masculine nouns used here: automobil/automobila, minibus/minibusa, autobus/autobusa)."""
    if lang == "en":
        return f"{n} {one if n == 1 else many}"
    singular = n % 10 == 1 and n % 100 != 11
    return f"{n} {bs_one if singular else bs_many}"


M: dict[str, dict[Lang, str]] = {
    # ---- Action names ----
    "action.led": {"en": "LED floodlights", "bs": "LED reflektori"},
    "action.solar": {"en": "Solar roof {kwp} kWp", "bs": "Solarni krov {kwp} kWp"},
    "action.insul": {"en": "Insulation + heat pump", "bs": "Izolacija + toplotna pumpa"},
    "action.carshare": {
        "en": "Car-sharing, fill the minibus",
        "bs": "Zajednički prijevoz, popunite minibus",
    },
    "action.lights_off": {
        "en": "Floodlights off when the pitch is empty (timer + rule)",
        "bs": "Gašenje reflektora kad je teren prazan (tajmer + pravilo)",
    },
    "action.heat_setpoint": {
        "en": "Heat 1 °C lower, and only when the hall is in use",
        "bs": "Grijanje 1 °C niže, i samo dok se dvorana koristi",
    },
    "action.kit_swap": {
        "en": "Kit-swap day: pass on outgrown kit",
        "bs": "Dan razmjene opreme: proslijedite opremu iz koje su djeca izrasla",
    },
    # ---- How each saving was calculated ----
    "basis.solar": {
        "en": "{kwp} kWp x {yield_} kWh/kWp (PVGIS) x {self_use} used on site",
        "bs": "{kwp} kWp × {yield_} kWh/kWp (PVGIS) × {self_use} iskorišteno na licu mjesta",
    },
    "basis.solar_capped": {
        "en": ", capped at the club's own use ({kwh} kWh)",
        "bs": ", ograničeno na vlastitu potrošnju kluba ({kwh} kWh)",
    },
    "basis.carshare": {
        "en": "{share} fewer car-km ({km} km)",
        "bs": "{share} manje kilometara automobilom ({km} km)",
    },
    "basis.kit": {
        "en": "{kits} kits a year passed on instead of bought new (~{price} KM and {kg} kg each)",
        "bs": "{kits} kompleta godišnje proslijeđeno umjesto kupljeno novo "
        "(~{price} KM i {kg} kg po kompletu)",
    },
    "basis.share_of": {"en": "{share} of {use} ({kwh} kWh)", "bs": "{share} od {use} ({kwh} kWh)"},
    "use.floodlights": {"en": "floodlights", "bs": "reflektora"},
    "use.heating": {"en": "heating", "bs": "grijanja"},
    "use.hall_and_other": {"en": "hall and other", "bs": "dvorane i ostalog"},
    # ---- Plan notes ----
    "note.not_paying": {
        "en": "The club doesn't pay the electricity bill: LED, solar and insulation would save "
        "money for the facility owner (e.g. the municipality). They are shown as a proposal to "
        "make, not as club savings.",
        "bs": "Klub ne plaća račun za struju: LED rasvjeta, solarni paneli i izolacija uštedjeli "
        "bi novac vlasniku objekta (npr. općini). Prikazani su kao prijedlog, a ne kao uštede "
        "kluba.",
    },
    "note.heating_not_electric": {
        "en": "Heating by {kind} isn't included: only electricity is counted. Better insulation "
        "would also lower that heating bill.",
        "bs": "Grijanje ({kind}) nije uključeno: računa se samo struja. Bolja izolacija bi "
        "smanjila i taj račun za grijanje.",
    },
    "heating.district": {"en": "district heating", "bs": "daljinsko grijanje"},
    "heating.gas": {"en": "gas", "bs": "plin"},
    "heating.wood": {"en": "wood", "bs": "drva"},
    "heating.other": {"en": "another source", "bs": "drugi izvor"},
    "heating.unknown": {"en": "an unknown system", "bs": "nepoznat izvor"},
    # ---- Affordability ----
    "aff.scope": {
        "en": "Electricity and away-travel fuel only (not staff, pitch rent or kit)",
        "bs": "Samo struja i gorivo za gostovanja (bez plata, najma terena i opreme)",
    },
    "aff.note": {
        "en": "Actions are estimated one by one; doing several together saves somewhat less "
        "than the sum, so 'after' is a best case.",
        "bs": "Mjere su procijenjene pojedinačno; više mjera zajedno uštedi nešto manje od "
        "zbira, pa je iznos „poslije” najbolji mogući slučaj.",
    },
    # ---- Energy method ----
    "energy.heating": {
        "en": "Heating spread by heating degree days (base {base} °C, Sarajevo monthly "
        "temperatures, Open-Meteo)",
        "bs": "Grijanje raspoređeno po stepen-danima grijanja (osnova {base} °C, mjesečne "
        "temperature Sarajeva, Open-Meteo)",
    },
    "energy.even": {
        "en": "Floodlights and hall spread evenly over 12 months (assumption)",
        "bs": "Reflektori i dvorana ravnomjerno raspoređeni na 12 mjeseci (pretpostavka)",
    },
    "energy.solar": {
        "en": "Solar: kWp x PVGIS monthly yield, {self_use} used on site (assumption)",
        "bs": "Solar: kWp × mjesečni prinos (PVGIS), {self_use} iskorišteno na licu mjesta "
        "(pretpostavka)",
    },
    "energy.sources": {
        "en": "Cost: Eurostat BiH non-household price; CO₂: Ember BiH grid intensity",
        "bs": "Trošak: Eurostat, cijena za BiH (nedomaćinstva); CO₂: Ember, intenzitet mreže BiH",
    },
    # ---- Quick start ----
    "quick.default_name": {"en": "My club", "bs": "Moj klub"},
    "quick.unknown_city": {
        "en": "Unknown city: {city}. Pick one from /api/cities or send lat/lon.",
        "bs": "Nepoznat grad: {city}. Odaberite grad sa /api/cities ili pošaljite lat/lon.",
    },
    "quick.location": {
        "en": "Location: centre of {city} (used to find nearby pitches and clubs).",
        "bs": "Lokacija: {city}, centar grada (za pronalazak obližnjih terena i klubova).",
    },
    "quick.bill": {
        "en": "Electricity: {bill} KM a month ÷ {price} KM/kWh ≈ {kwh} kWh a year.",
        "bs": "Struja: {bill} KM mjesečno ÷ {price} KM/kWh ≈ {kwh} kWh godišnje.",
    },
    "quick.no_bill": {
        "en": "Electricity: no bill given, so a rough estimate of {per_team} kWh per team "
        "({kwh} kWh a year). Enter your bill for a real number.",
        "bs": "Struja: račun nije unesen, pa je ovo gruba procjena od {per_team} kWh po ekipi "
        "({kwh} kWh godišnje). Unesite račun za stvarni iznos.",
    },
    "quick.split": {
        "en": "Split of electricity (floodlights / heating / hall) is typical, not measured.",
        "bs": "Podjela potrošnje (reflektori / grijanje / dvorana) je tipična, nije izmjerena.",
    },
    "quick.split_no_heating": {
        "en": "Split of electricity (floodlights / heating / hall) is typical, not measured; "
        "heating is not electric so it isn't counted.",
        "bs": "Podjela potrošnje (reflektori / grijanje / dvorana) je tipična, nije izmjerena; "
        "grijanje nije na struju, pa se ne računa.",
    },
    "quick.heating_unknown": {
        "en": "Heating type unknown: we assume it isn't electric. Change it if it is.",
        "bs": "Vrsta grijanja nepoznata: pretpostavljamo da nije na struju. Promijenite ako jeste.",
    },
    "quick.away_games": {
        "en": "Away games: assumed {n} per team per season.",
        "bs": "Gostovanja: pretpostavljeno {n} po ekipi u sezoni.",
    },
    "quick.distance": {
        "en": "Distance to away games: assumed {km} km one way.",
        "bs": "Udaljenost do gostovanja: pretpostavljeno {km} km u jednom smjeru.",
    },
    "quick.vehicles": {
        "en": "Vehicles per trip for {people} people ({transport}): {minibuses}, {cars}.",
        "bs": "Vozila po putovanju za {people} osoba ({transport}): {minibuses}, {cars}.",
    },
    "transport.cars": {"en": "cars", "bs": "automobili"},
    "transport.minibus": {"en": "minibus", "bs": "minibus"},
    "transport.mixed": {"en": "mixed", "bs": "kombinovano"},
    "quick.not_paying": {
        "en": "The club doesn't pay electricity: facility upgrades will be shown as proposals "
        "for the facility owner.",
        "bs": "Klub ne plaća struju: unapređenja objekta bit će prikazana kao prijedlozi za "
        "vlasnika objekta.",
    },
    # ---- Travel ----
    "travel.current": {"en": "Current mix of vehicles", "bs": "Trenutna kombinacija vozila"},
    "travel.cars": {"en": "{cars} ({occ} per car)", "bs": "{cars} ({occ} po automobilu)"},
    "travel.minibuses": {"en": "{minibuses} ({seats} seats)", "bs": "{minibuses} ({seats} mjesta)"},
    "travel.coach": {
        "en": "{coaches} hired ({seats} seats)",
        "bs": "{coaches}, najam ({seats} mjesta)",
    },
    "travel.coach_shared": {"en": ", shared by two clubs", "bs": ", dijele dva kluba"},
    "travel.no_partner": {
        "en": "No named partner club found nearby; a partner is assumed.",
        "bs": "U blizini nije pronađen imenovani partnerski klub; partner je pretpostavljen.",
    },
    "trip.rail": {"en": "Train (scheduled service)", "bs": "Voz (redovna linija)"},
    "trip.per_car_km": {"en": "{f} kg CO2e per car-km", "bs": "{f} kg CO2e po km automobila"},
    "trip.per_van_km": {"en": "{f} kg CO2e per van-km", "bs": "{f} kg CO2e po km minibusa"},
    "trip.per_coach_km": {
        "en": "{f} kg CO2e per coach-km ({pkm} per passenger-km x {occ} avg passengers)",
        "bs": "{f} kg CO2e po km autobusa ({pkm} po putničkom km × {occ} prosječnih putnika)",
    },
    "trip.per_pkm": {"en": "{f} kg CO2e per passenger-km", "bs": "{f} kg CO2e po putničkom km"},
    # ---- Share / distance ----
    "share.note": {
        "en": "Partners = named stadiums/sports centres nearby (OSM): a heuristic for clubs, "
        "verify locally",
        "bs": "Partneri = imenovani stadioni/sportski centri u blizini (OSM): procjena za "
        "klubove, provjerite lokalno",
    },
    "distance.note": {
        "en": "Straight-line (haversine) distance; road distance estimated as straight x 1.3",
        "bs": "Udaljenost zračnom linijom (haversine); cestovna udaljenost procijenjena kao "
        "zračna × 1,3",
    },
    # ---- Check a bill ----
    "bill.err_electricity": {
        "en": "An electricity bill needs the kWh and the billing month.",
        "bs": "Za račun za struju potrebni su kWh i mjesec obračuna.",
    },
    "bill.err_fuel": {
        "en": "A fuel receipt needs litres, the amount and the fuel type.",
        "bs": "Za račun za gorivo potrebni su litri, iznos i vrsta goriva.",
    },
    "bill.scale_warning": {
        "en": "The bill is far from the club's profile (x{raw}); the yearly estimate was limited "
        "to x{used}. Check the kWh and the club's yearly figures.",
        "bs": "Račun znatno odstupa od profila kluba (x{raw}); godišnja procjena je ograničena na "
        "x{used}. Provjerite kWh i godišnje podatke kluba.",
    },
    "bill.price.unit_price": {
        "en": "price per kWh printed on the bill",
        "bs": "cijena po kWh štampana na računu",
    },
    "bill.price.total_per_kwh": {
        "en": "bill total divided by kWh (includes fixed charges, so savings from using less "
        "electricity may be slightly overstated)",
        "bs": "ukupan iznos računa podijeljen sa kWh (uključuje fiksne naknade, pa uštede od manje "
        "potrošnje mogu biti malo precijenjene)",
    },
    "bill.price.assumed": {
        "en": "assumed Eurostat price for BiH (the bill gave no price)",
        "bs": "pretpostavljena cijena za BiH (Eurostat), jer račun ne sadrži cijenu",
    },
    "bill.price.fuel": {
        "en": "electricity price unchanged (a fuel receipt says nothing about it)",
        "bs": "cijena struje nepromijenjena (račun za gorivo ne govori ništa o njoj)",
    },
    "bill.based_on_electricity": {
        "en": "One bill (month {month}): the club's yearly electricity is scaled from this single "
        "month. Each further bill makes the estimate firmer.",
        "bs": "Jedan račun (mjesec {month}): godišnja potrošnja kluba preračunata je iz ovog "
        "jednog mjeseca. Svaki sljedeći račun čini procjenu pouzdanijom.",
    },
    "bill.based_on_fuel": {
        "en": "One {fuel} receipt: the pump price replaces the assumed one in the cost of a "
        "{vehicle} kilometre.",
        "bs": "Jedan račun za gorivo ({fuel}): cijena sa pumpe zamjenjuje pretpostavljenu u "
        "trošku po kilometru ({vehicle}).",
    },
    "fuel.diesel": {"en": "diesel", "bs": "dizel"},
    "fuel.petrol": {"en": "petrol", "bs": "benzin"},
    "vehicle.car": {"en": "car", "bs": "automobil"},
    "vehicle.minibus": {"en": "minibus", "bs": "minibus"},
    "waste.temp.typical": {
        "en": "typical Sarajevo temperature for the month (Open-Meteo 2024-2025)",
        "bs": "uobičajena temperatura u Sarajevu za taj mjesec (Open-Meteo 2024-2025)",
    },
    "waste.temp.supplied": {
        "en": "temperature supplied for the bill month",
        "bs": "unesena temperatura za mjesec računa",
    },
    "waste.basis": {
        "en": "Expected = floodlights and hall spread evenly over 12 months + yearly heating "
        "spread by heating degree days (base {base} °C), from the club's own yearly figures",
        "bs": "Očekivano = reflektori i dvorana ravnomjerno na 12 mjeseci + godišnje grijanje "
        "raspoređeno po stepen-danima grijanja (osnova {base} °C), iz godišnjih podataka kluba",
    },
    "check.other": {
        "en": "This does not look like an electricity bill or receipt.",
        "bs": "Ovo ne izgleda kao račun za struju ili gorivo.",
    },
    "check.uncertain": {
        "en": "Some numbers are uncertain: check every number against the bill.",
        "bs": "Neki brojevi su nesigurni: provjerite svaki broj na računu.",
    },
    "check.bad_month": {
        "en": "The billing month is not a valid month.",
        "bs": "Mjesec obračuna nije ispravan.",
    },
    "check.future": {
        "en": "The billing period is in the future: check the month and year.",
        "bs": "Obračunski period je u budućnosti: provjerite mjesec i godinu.",
    },
    "check.no_kwh": {
        "en": "No kWh found: type in the consumption from the bill.",
        "bs": "Nema kWh: unesite potrošnju sa računa.",
    },
    "check.kwh_implausible": {
        "en": "The kWh figure looks implausible for a club: check it.",
        "bs": "Iznos kWh izgleda nevjerovatno za klub: provjerite ga.",
    },
    "check.price_unusual": {
        "en": "Total ÷ kWh is {price} KM/kWh, which looks unusual: check both numbers.",
        "bs": "Ukupno ÷ kWh iznosi {price} KM/kWh, što izgleda neobično: provjerite oba broja.",
    },
    "check.unit_price_unusual": {
        "en": "The printed price per kWh looks unusual: check it.",
        "bs": "Štampana cijena po kWh izgleda neobično: provjerite je.",
    },
    "check.fuel_missing": {
        "en": "Litres or amount not found: type them in from the receipt.",
        "bs": "Nedostaju litri ili iznos: unesite ih sa računa.",
    },
    "check.per_litre_unusual": {
        "en": "{price} KM per litre looks unusual: check litres and amount.",
        "bs": "{price} KM po litru izgleda neobično: provjerite litre i iznos.",
    },
    "check.fuel_type": {
        "en": "Only diesel and petrol receipts can update the travel plan.",
        "bs": "Samo računi za dizel i benzin mogu ažurirati plan putovanja.",
    },
}

# Nouns with Bosnian counting forms (see plural()).
NOUNS: dict[str, tuple[str, str, str, str]] = {
    "car": ("car", "cars", "automobil", "automobila"),
    "minibus": ("minibus", "minibuses", "minibus", "minibusa"),
    "coach": ("coach", "coaches", "autobus", "autobusa"),
}


def t(key: str, lang: Lang, **kw: object) -> str:
    return M[key][lang].format(**kw)


def count(n: int, noun: str, lang: Lang) -> str:
    return plural(n, lang, *NOUNS[noun])
