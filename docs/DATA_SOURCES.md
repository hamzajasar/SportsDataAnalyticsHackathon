# Data sources — Topic 6: The Sustainable Sports Club

**Every source below must be named on the final slide** (organisers' rule). Copy the "Credit line".

| Dataset | Used for | Licence | Credit line | In repo |
|---|---|---|---|---|
| UK Government GHG Conversion Factors 2025 (flat file) | kg CO₂e per car/van-km, coach/rail passenger-km, fuel, waste, material production | Open Government Licence v3.0 | "Contains public sector information licensed under the Open Government Licence v3.0 — UK DESNZ GHG Conversion Factors 2025" | Derived subset in `backend/app/reference/emission_factors.csv` |
| Ember — yearly electricity data (via Our World in Data) | gCO₂/kWh per country & year; electricity mix by source | CC BY 4.0 | "Ember (2026); Our World in Data" | `backend/app/reference/grid_intensity.csv`, `electricity_mix.csv` |
| Open-Meteo historical weather | Daily temperature/precipitation for Sarajevo (heating vs weather) | CC BY 4.0 | "Weather data by Open-Meteo.com" | Raw only (`make data`) |
| OpenStreetMap (Overpass) | ~3,700 pitches/stadiums/halls in BiH: distances, sharing facilities | ODbL | "© OpenStreetMap contributors" | Raw only (`make data`); anything we publish from it stays ODbL |
| Organisers' synthetic data pack (e.g. `equipment.csv`) | Club-level equipment / energy / travel records | Hackathon use | "Sports Analytics Hackathon synthetic data pack" | Put in `data/raw/pack/` (git-ignored) |

## How to get the data
```bash
make data        # downloads all open datasets above into data/raw/sustainability/
make reference   # rebuilds the small committed tables in backend/app/reference/
make profile     # data report -> data/processed/_profile.md
```

## Method notes (keep honest — jury includes a data professional)
- **UK factors applied to BiH:** there is no BiH-specific transport factor set; UK vehicle factors are a reasonable proxy for fuel combustion (same physics), but BiH fleet is older → our travel numbers are likely **under**estimates. Say so.
- **Electricity** uses BiH's own grid intensity (Ember), not UK electricity factors.
- **Waste vs material factors:** disposal factors only cover end of life (recycling ≈ transport only). The footprint of equipment is in *production* — use `material_*_new` vs `material_*_reused` for "buy new vs re-use".
- **Kit weight** (kg per kit) is our assumption, editable in the UI.
- Car occupancy, minibus seats (8) are assumptions, shown next to every result.
