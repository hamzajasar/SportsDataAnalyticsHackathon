"""Download the open datasets for Topic 6 (The Sustainable Sports Club) into data/raw/.

Usage: make data            (skips files that already exist)
       make data FORCE=1    (re-download everything)

Every source is free and needs no login. Licences/attribution are listed in docs/DATA_SOURCES.md
and MUST be credited on the final slide.
"""

import csv
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from app.core.config import settings

OUT = settings.data_dir / "raw" / "sustainability"
FORCE = os.getenv("FORCE") == "1"
UA = {"User-Agent": "sports-analytics-hackathon/0.1 (data download script)"}

# Sarajevo (city centre). Add more places here if the club(s) are elsewhere.
PLACES = {"sarajevo": (43.8563, 18.4131)}
WEATHER_START, WEATHER_END = "2015-01-01", "2025-12-31"


def pvgis(path: Path) -> None:
    # PVGIS (EU JRC), free to reuse with source acknowledged: yearly kWh per kWp, Sarajevo
    lat, lon = PLACES["sarajevo"]
    params = {"lat": lat, "lon": lon, "peakpower": 1, "loss": 14, "angle": 35, "aspect": 0}
    url = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?" + urllib.parse.urlencode(
        {**params, "outputformat": "json"}
    )
    path.write_bytes(fetch(url, timeout=90))


OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
OVERPASS_QUERY = """[out:json][timeout:60];
area["ISO3166-1"="BA"][admin_level=2]->.ba;
nwr["leisure"~"^(pitch|stadium|sports_centre|sports_hall)$"](area.ba);
out center tags;"""


def fetch(url: str, *, data: bytes | None = None, timeout: int = 60, tries: int = 3) -> bytes:
    last: Exception | None = None
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # network hiccups on venue Wi-Fi
            last = e
            if attempt < tries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"{url}: {last}")


def step(name: str, path: Path, fn) -> bool:
    if path.exists() and not FORCE:
        print(f"  ✓ {name:<38} (exists) {path.relative_to(settings.data_dir)}")
        return True
    print(f"  … {name:<38}", end="", flush=True)
    try:
        fn(path)
        print(f"\r  ✓ {name:<38} {path.relative_to(settings.data_dir)}")
        return True
    except Exception as e:
        print(f"\r  ✗ {name:<38} FAILED: {e}")
        return False


def ghg_factors(path: Path) -> None:
    # UK Government GHG conversion factors 2025, flat file (Open Government Licence v3.0)
    url = (
        "https://assets.publishing.service.gov.uk/media/6846b6ea57f3515d9611f0dd/"
        "ghg-conversion-factors-2025-flat-format.xlsx"
    )
    path.write_bytes(fetch(url, timeout=90))


def carbon_intensity(path: Path) -> None:
    # Ember (via Our World in Data): gCO2/kWh of electricity per country & year (CC BY 4.0)
    url = (
        "https://ourworldindata.org/grapher/carbon-intensity-electricity.csv"
        "?v=1&csvType=full&useColumnShortNames=true"
    )
    path.write_bytes(fetch(url))


def electricity_mix(path: Path) -> None:
    # Ember (via Our World in Data): share of electricity by source per country & year (CC BY 4.0)
    url = (
        "https://ourworldindata.org/grapher/share-elec-by-source.csv"
        "?v=1&csvType=full&useColumnShortNames=true"
    )
    path.write_bytes(fetch(url))


def weather(place: str, lat: float, lon: float):
    def run(path: Path) -> None:
        # Open-Meteo historical archive (CC BY 4.0), daily values
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": WEATHER_START,
            "end_date": WEATHER_END,
            "daily": "temperature_2m_mean,temperature_2m_min,temperature_2m_max,precipitation_sum",
            "timezone": "Europe/Sarajevo",
        }
        url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
        d = json.loads(fetch(url, timeout=90))["daily"]
        cols = list(d.keys())
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["place", *cols])
            for row in zip(*(d[c] for c in cols), strict=True):
                w.writerow([place, *row])

    return run


def osm_sports_facilities(path: Path) -> None:
    # OpenStreetMap via Overpass (ODbL — credit "© OpenStreetMap contributors")
    body = urllib.parse.urlencode({"data": OVERPASS_QUERY}).encode()
    errors = []
    for ep in OVERPASS_MIRRORS:
        try:
            elements = json.loads(fetch(ep, data=body, timeout=75, tries=1))["elements"]
            break
        except Exception as e:
            errors.append(str(e))
    else:
        raise RuntimeError("all Overpass mirrors failed: " + " | ".join(errors))

    fields = ["osm_type", "osm_id", "leisure", "sport", "name", "lat", "lon", "city", "surface"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    for el in elements:
        tags = el.get("tags", {})
        lat = el.get("lat", el.get("center", {}).get("lat"))
        lon = el.get("lon", el.get("center", {}).get("lon"))
        w.writerow(
            {
                "osm_type": el["type"],
                "osm_id": el["id"],
                "leisure": tags.get("leisure"),
                "sport": tags.get("sport"),
                "name": tags.get("name"),
                "lat": lat,
                "lon": lon,
                "city": tags.get("addr:city"),
                "surface": tags.get("surface"),
            }
        )
    path.write_text(buf.getvalue())


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Downloading Topic 6 open data into {OUT}")
    steps = [
        (
            "GHG conversion factors 2025 (UK)",
            OUT / "ghg_conversion_factors_2025_flat.xlsx",
            ghg_factors,
        ),
        (
            "Electricity carbon intensity (Ember)",
            OUT / "carbon_intensity_electricity.csv",
            carbon_intensity,
        ),
        (
            "Electricity mix by source (Ember)",
            OUT / "electricity_mix_by_source.csv",
            electricity_mix,
        ),
        *[
            (f"Daily weather {p} (Open-Meteo)", OUT / f"weather_{p}_daily.csv", weather(p, *ll))
            for p, ll in PLACES.items()
        ],
        ("Solar yield Sarajevo (PVGIS)", OUT / "pvgis_sarajevo.json", pvgis),
        (
            "BiH sports facilities (OpenStreetMap)",
            OUT / "osm_ba_sports_facilities.csv",
            osm_sports_facilities,
        ),
    ]
    ok = [step(name, path, fn) for name, path, fn in steps]
    print(f"\n{sum(ok)}/{len(ok)} datasets ready. Next: make profile")
    if not all(ok):
        print("Re-run `make data` later for the failed ones (public APIs are sometimes busy).")
        sys.exit(1)


if __name__ == "__main__":
    main()
