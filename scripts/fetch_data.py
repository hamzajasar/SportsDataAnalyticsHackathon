"""Fetch the external sources for Club Footprint into data/raw and data/clean.
Stdlib only. Run: python scripts/fetch_data.py
"""
import csv, io, json, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, CLEAN = ROOT / "data" / "raw", ROOT / "data" / "clean"
RAW.mkdir(parents=True, exist_ok=True)
CLEAN.mkdir(parents=True, exist_ok=True)


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "club-footprint-hackathon"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def write_json(name, obj):
    (CLEAN / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", CLEAN / name)


# 1. Ember: CO2 per kWh (gCO2e/kWh), BiH vs HR vs EU
def ember():
    url = "https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv"
    raw = get(url)
    (RAW / "ember_yearly.csv").write_bytes(raw)
    rows = csv.DictReader(io.StringIO(raw.decode("utf-8")))
    keep = {"Bosnia Herzegovina": "BiH", "Croatia": "HR", "EU": "EU"}
    out = {}
    for r in rows:
        if r["Area"] in keep and r["Electricity source"] == "Total generation" and r["Year"] >= "2015"                 and r["Emissions intensity (gCO2e/kWh)"]:
            out.setdefault(keep[r["Area"]], {})[r["Year"]] = round(float(r["Emissions intensity (gCO2e/kWh)"]), 1)
    write_json("grid_factor.json", {
        "unit": "gCO2e/kWh", "values": out,
        "source": "Ember yearly electricity data", "licence": "CC BY 4.0",
        "url": "https://ember-energy.org/data/yearly-electricity-data/"})


# 2. Open-Meteo: Sarajevo monthly mean temperature (2024-2025)
def meteo():
    q = urllib.parse.urlencode({
        "latitude": 43.8563, "longitude": 18.4131,
        "start_date": "2024-01-01", "end_date": "2025-12-31",
        "daily": "temperature_2m_mean", "timezone": "Europe/Sarajevo"})
    d = json.loads(get("https://archive-api.open-meteo.com/v1/archive?" + q))
    (RAW / "openmeteo_sarajevo_daily.json").write_text(json.dumps(d), encoding="utf-8")
    by_month = {}
    for day, t in zip(d["daily"]["time"], d["daily"]["temperature_2m_mean"]):
        if t is not None:
            by_month.setdefault(int(day[5:7]), []).append(t)
    write_json("sarajevo_monthly_temp.json", {
        "monthly_mean_c": {m: round(sum(v) / len(v), 1) for m, v in sorted(by_month.items())},
        "source": "Open-Meteo historical weather", "licence": "CC BY 4.0",
        "url": "https://open-meteo.com/"})


# 3. OSM via Overpass: pitches/halls in BiH
def osm():
    query = ('[out:json][timeout:60];area["ISO3166-1"="BA"][admin_level=2]->.ba;'
             'nwr["leisure"~"^(pitch|stadium|sports_centre|sports_hall)$"](area.ba);out center;')
    body = urllib.parse.urlencode({"data": query}).encode()
    for ep in ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
               "https://overpass.private.coffee/api/interpreter"):
        try:
            d = json.loads(get(ep, body))
            break
        except Exception as ex:
            print("overpass", ep, "failed:", ex)
    else:
        raise RuntimeError("all Overpass endpoints failed")
    (RAW / "osm_bih_sport.json").write_text(json.dumps(d), encoding="utf-8")
    feats = []
    for e in d["elements"]:
        lat = e.get("lat") or e.get("center", {}).get("lat")
        lon = e.get("lon") or e.get("center", {}).get("lon")
        if lat is None:
            continue
        t = e.get("tags", {})
        feats.append({"id": f'{e["type"]}/{e["id"]}', "lat": lat, "lon": lon,
                      "leisure": t.get("leisure"), "sport": t.get("sport"), "name": t.get("name")})
    write_json("osm_sport_venues.json", {
        "venues": feats, "source": "OpenStreetMap contributors via Overpass",
        "licence": "ODbL", "url": "https://www.openstreetmap.org/copyright"})


# 4. PVGIS: yearly kWh per installed kWp, Sarajevo
def pvgis():
    q = urllib.parse.urlencode({"lat": 43.8563, "lon": 18.4131, "peakpower": 1, "loss": 14,
                                "angle": 35, "aspect": 0, "outputformat": "json"})
    d = json.loads(get("https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?" + q))
    (RAW / "pvgis_sarajevo.json").write_text(json.dumps(d), encoding="utf-8")
    t = d["outputs"]["totals"]["fixed"]
    write_json("pv_yield.json", {
        "kwh_per_kwp_year": round(t["E_y"]), "monthly_kwh_per_kwp": {
            str(m["month"]): round(m["E_m"], 1) for m in d["outputs"]["monthly"]["fixed"]},
        "assumptions": {"tilt_deg": 35, "azimuth": "south", "system_loss_pct": 14},
        "source": "PVGIS (EU JRC)", "credit": "PVGIS © European Communities",
        "url": "https://re.jrc.ec.europa.eu/pvg_tools/en/"})


if __name__ == "__main__":
    for fn in (ember, meteo, osm, pvgis):
        try:
            fn()
        except Exception as ex:
            print(f"{fn.__name__} FAILED: {ex}")
