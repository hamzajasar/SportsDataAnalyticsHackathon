# Data sources — Topic 6: The Sustainable Sports Club

**Every source below must be named on the final slide** (organisers' rule). Copy the "Credit line".

| Dataset | Used for | Licence | Credit line | In repo |
|---|---|---|---|---|
| UK Government GHG Conversion Factors 2025 (flat file) | kg CO₂e per car/van-km, coach/rail passenger-km, fuel, waste, material production | Open Government Licence v3.0 | "Contains public sector information licensed under the Open Government Licence v3.0 — UK DESNZ GHG Conversion Factors 2025" | Derived subset in `backend/app/reference/emission_factors.csv` |
| Ember — yearly electricity data (via Our World in Data) | gCO₂/kWh per country & year; electricity mix by source | CC BY 4.0 | "Ember (2026); Our World in Data" | `backend/app/reference/grid_intensity.csv`, `electricity_mix.csv` |
| Open-Meteo historical weather | Sarajevo monthly mean temperature (heating shape) | CC BY 4.0 | "Weather data by Open-Meteo.com" | `backend/app/reference/sarajevo_temperature.csv` |
| OpenStreetMap (Overpass) | 3,705 pitches/stadiums/halls in BiH: distances, sharing facilities | ODbL | "© OpenStreetMap contributors" | `backend/app/reference/sport_venues_bih.csv`; anything we publish from it stays ODbL |
| PVGIS (EU JRC) | Solar yield per installed kWp, Sarajevo, by month | Free reuse with credit | "PVGIS © European Communities" | `backend/app/reference/pv_yield_sarajevo.csv` |
| Price assumptions (electricity, fuel) | KM costs, payback | — | Mark as assumptions on the slide | `backend/app/reference/cost_assumptions.csv` (**verify before the pitch**) |
| Organisers' synthetic data pack | Club-level energy / travel / children (main club data) | Hackathon use | "Sports Analytics Hackathon synthetic data pack" | Raw in `data/raw/pack/` (ignored) → cleaned into `data/clean/` |

The full list with credit lines is also served by the API at `/api/sources` (from `data/clean/sources.json`).

## How to get the data
```bash
make data        # downloads all open datasets (raw -> data/raw, cleaned -> data/clean)
make reference   # rebuilds ALL committed tables in backend/app/reference/ (reproducible, no diff if unchanged)
make profile     # data report -> data/processed/_profile.md
```

## Method notes (keep honest — jury includes a data professional)
- **UK factors applied to BiH:** there is no BiH-specific transport factor set; UK vehicle factors are a reasonable proxy for fuel combustion (same physics), but BiH fleet is older → our travel numbers are likely **under**estimates. Say so.
- **Electricity** uses BiH's own grid intensity (Ember), not UK electricity factors.
- **Waste vs material factors:** disposal factors only cover end of life (recycling ≈ transport only). The footprint of equipment is in *production* — use `material_*_new` vs `material_*_reused` for "buy new vs re-use".
- **Kit weight** (kg per kit) is our assumption, editable in the UI.
- Car occupancy, minibus seats (8) are assumptions, shown next to every result.
- **Hired coach is counted per vehicle**, not per passenger: UK publishes coach CO₂ per passenger-km at
  average occupancy, but a hired coach emits the same with 18 or 50 people. We use
  0.02776 kg/passenger-km × 35 assumed average passengers = 0.97 kg per coach-km. Train stays per
  passenger (scheduled service runs anyway).
