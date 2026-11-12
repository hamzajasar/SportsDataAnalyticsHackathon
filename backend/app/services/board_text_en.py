"""Draft board decision in English: the twin of board_text.py (Bosnian), same sections and figures.

A template, not generated text: every figure is inserted by code from the analysis.
"""

from datetime import date

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]  # fmt: skip

CHECKS = {
    "floodlights": "floodlight timers, and whether lights stay on after training",
    "heating": "the heating set-point, and whether unused rooms or the hall are heated",
    "baseload": "the previous bill and the meter reading, to rule out a billing error",
}
PRICE_SOURCES = {
    "unit_price": "price per kWh printed on the bill",
    "total_per_kwh": "bill total divided by kWh, including fixed charges",
    "assumed": "assumed BiH price (Eurostat), as the bill shows no price",
    "fuel": "electricity price unchanged",
}
SOURCES = (
    "Ember (grid emissions), Eurostat (electricity price), Open-Meteo (temperature), "
    "PVGIS (solar potential), UK GHG 2025 (vehicle emission factors)."
)


def fmt(x: float, decimals: int = 0) -> str:
    return f"{x:,.{decimals}f}"


def _payback(a: dict) -> str:
    if a["payback_years"] is None:
        return "payback cannot be calculated"
    if a["cost_km"] == 0:
        return "pays back immediately"
    return f"pays back in {fmt(a['payback_years'], 1)} years"


def _measures(top: list[dict]) -> list[str]:
    lines = ["3. Proposed measures (ranked by payback period)"]
    for i, a in enumerate(top, 1):
        cost = "no cost" if a["cost_km"] == 0 else f"cost {fmt(a['cost_km'])} KM"
        lines.append(
            f"   {i}. {a['name']}: {cost}, saves {fmt(a['saves_km_year'])} KM a year, {_payback(a)}"
        )
    return lines


def _savings(plan: dict, club: dict) -> list[str]:
    after, before = plan["after"], plan["before"]
    lines = [
        f"   - Possible total saving: about {fmt(after['total_saves_km_year'])} KM and "
        f"{fmt(after['total_saves_t_co2_year'], 1)} t CO₂ a year.",
        f"   - The membership fee per child could be about "
        f"{fmt(after['fee_drop_per_child_km'], 1)} KM a year lower ({fmt(club['children'])} "
        "children).",
    ]
    if round(before["total_saves_km_year"]) != round(after["total_saves_km_year"]):
        lines.append(
            f"   - Before this bill, the estimated saving was "
            f"{fmt(before['total_saves_km_year'])} KM a year."
        )
    return lines


def _footer(analysis: dict, based_on: str) -> list[str]:
    lines = ["", "Notes:", f"   - {based_on}", f"   - Sources: {SOURCES}"]
    if analysis["illustrative_club"]:
        lines.append(
            "   - The club data (number of children, yearly use, travel) is ILLUSTRATIVE and "
            "does not describe a real club."
        )
    lines += ["", "Chair of the Board: ______________________"]
    return lines


def _header(club: dict, analysis: dict, today: date) -> list[str]:
    lines = ["DRAFT DECISION OF THE CLUB BOARD", club["name"], f"Date: {today:%d %B %Y}", ""]
    if analysis["illustrative_club"]:
        lines += [
            "NOTE: This is an ILLUSTRATIVE example based on a sample club, not a real decision.",
            "",
        ]
    return lines


def _electricity_text(analysis: dict, club: dict, bill: dict, today: date) -> str:
    w, plan = analysis["waste"], analysis["plan"]
    m = bill["period_month"]
    year = f" {bill['period_year']}" if bill.get("period_year") else ""
    amount = f", amount {fmt(bill['amount_km'], 2)} KM" if bill.get("amount_km") else ""
    pct = w["difference_pct"]
    temp_src = (
        "typical for that month"
        if w.get("temperature_source_id", "typical") == "typical"
        else "actual temperature of the month"
    )
    verdict = {
        "normal": "Use is within the expected range (±10%).",
        "above": (
            f"Use is {fmt(pct, 1)}% higher than expected (about {fmt(w['excess_kwh'])} kWh, "
            f"or {fmt(w['excess_km'])} KM too much this month)."
        ),
        "high": (
            f"Use is much higher than expected: {fmt(pct or 0, 1)}% (about "
            f"{fmt(w['excess_kwh'])} kWh, or {fmt(w['excess_km'])} KM too much this month). "
            "This needs checking."
        ),
        "below": f"Use is {fmt(abs(pct or 0), 1)}% lower than expected.",
        "unknown": "Expected use cannot be calculated for this club.",
    }[w["status"]]

    lines = _header(club, analysis, today)
    lines += [
        f"Basis: electricity bill for {MONTHS[m - 1]}{year}: {fmt(bill['kwh'])} kWh{amount}.",
        "",
        "1. Finding",
        f"   - Use in {MONTHS[m - 1]} was {fmt(w['actual_kwh'])} kWh. From the club's yearly "
        f"figures and the Sarajevo temperature ({fmt(w['temperature_c'], 1)} °C, {temp_src}) "
        f"about {fmt(w['expected_kwh'])} kWh was expected.",
        f"   - {verdict}",
    ]
    if w["suggestions"]:
        lines.append("   - Check first:")
        lines += [f"       * {CHECKS[s]}" for s in w["suggestions"]]
    lines += [
        "",
        "2. Yearly estimate",
        f"   - Based on this bill, yearly use is estimated at about "
        f"{fmt(plan['annual_kwh_estimate'])} kWh (before: "
        f"{fmt(plan['before']['electricity_kwh_year'])} kWh).",
        f"   - Electricity price used: {fmt(plan['price_km_per_kwh_used'], 3)} KM/kWh "
        f"({PRICE_SOURCES[plan['price_source_id']]}).",
    ]
    lines += _savings(plan, club)
    lines += [""] + _measures(plan["after"]["top_actions"])
    top = plan["after"]["top_actions"][0]
    first = (
        "the possible causes of excess use listed above are checked within 15 days and the "
        "Board is informed of the findings;"
        if w["status"] in ("above", "high")
        else "electricity use continues to be monitored every month;"
    )
    second = (
        f"the measure “{top['name']}” is introduced immediately;"
        if top["cost_km"] == 0
        else f"work starts on the measure “{top['name']}”: collect at least two "
        "quotes by ____________;"
    )
    lines += [
        "",
        "4. Proposed decision",
        "   The Board decides that:",
        f"   1. {first}",
        f"   2. {second}",
        "   3. every monthly bill is recorded and the savings estimate updated.",
    ]
    return "\n".join(lines + _footer(analysis, _based_on(analysis, bill)))


def _fuel_text(analysis: dict, club: dict, bill: dict, today: date) -> str:
    f, plan = analysis["fuel"], analysis["plan"]
    diff = f["difference_pct"]
    relation = f"{fmt(abs(diff), 1)}% {'higher' if diff > 0 else 'lower'} than our assumption"
    lines = _header(club, analysis, today)
    lines += [
        f"Basis: fuel receipt ({f['fuel_type']}): {fmt(f['litres'], 1)} l, "
        f"{fmt(f['amount_km'], 2)} KM.",
        "",
        "1. Finding",
        f"   - The price on the receipt is {fmt(f['price_km_per_litre'], 2)} KM/l; that is "
        f"{relation} ({fmt(f['assumed_km_per_litre'], 2)} KM/l).",
        "",
        "2. Effect on the plan",
        f"   - Yearly fuel cost for away games: {fmt(plan['after']['travel_km_cost_year'])} KM "
        f"(before: {fmt(plan['before']['travel_km_cost_year'])} KM).",
    ]
    lines += _savings(plan, club)
    lines += [""] + _measures(plan["after"]["top_actions"])
    lines += [
        "",
        "4. Proposed decision",
        "   The Board decides that:",
        "   1. fuel receipts for away games are recorded and attached to travel expense claims;",
        "   2. shared transport with a partner club is considered, to reduce costs;",
        "   3. the savings estimate is updated after every new bill.",
    ]
    return "\n".join(lines + _footer(analysis, _based_on(analysis, bill)))


def decision_text_en(analysis: dict, club: dict, bill: dict, today: date | None = None) -> str:
    today = today or date.today()
    if analysis["kind"] == "electricity":
        return _electricity_text(analysis, club, bill, today)
    return _fuel_text(analysis, club, bill, today)


def _based_on(analysis: dict, bill: dict) -> str:
    if analysis["kind"] == "electricity":
        m = MONTHS[bill["period_month"] - 1]
        return (
            f"The estimate is based on one bill ({m}) and the club's yearly figures; yearly use "
            "is scaled from this single month. Each further bill makes it more accurate."
        )
    return (
        f"The estimate is based on one fuel receipt ({bill.get('fuel_type') or 'fuel'}); the "
        "fuel price has been updated."
    )
