# Work plan — 3 people, Topic 6 (The Sustainable Sports Club)

Three lanes that touch different folders, so you rarely block each other or hit merge conflicts.
Assign a name to each lane. Every item below is one `feature/<name>` branch → PR into `dev`.

| Lane | Owns | Folders | Judging criteria it drives |
|---|---|---|---|
| **A · Data & Analysis** | Data quality, models, the numbers | `notebooks/`, `backend/app/services/`, `backend/scripts/`, `docs/DATA_SOURCES.md` | Data quality & soundness, Relevance |
| **B · Backend & Integration** | API, database, deployment | `backend/app/api/`, `schemas/`, `models/`, `migrations/`, `render.yaml` | Technical execution, Feasibility |
| **C · Frontend & Story** | UI, charts, map, pitch, demo | `frontend/src/`, `README.md`, slides | Presentation, Innovation, Impact & inclusion |

## How the lanes connect (the contract)
```
A: services/*.py  (pure functions, tested)   ──►   B: api/routes/*.py + schemas  ──make gen-api──►  C: api/queries.ts + pages
```
- **B ships the endpoint shape first**, even returning fixed example data, and runs `make gen-api`. C can then build the UI right away while A finishes the real logic behind it.
- Shapes change only in `backend/app/schemas/`, and whoever changes one runs `make gen-api` in the same PR.

## Backlog (in priority order per lane)

### A · Data & Analysis
1. `feature/pack-ingest`: load the organisers' synthetic pack (`data/raw/pack/`), `make profile`, clean it, document every cleaning step (needed for the Methodology page and the jury).
2. `feature/heating-weather`: monthly energy use vs Sarajevo temperature (Open-Meteo): regression in `statsmodels`, "expected vs actual" per month, flag waste. Report R²/residuals honestly.
3. `feature/action-plan-model`: rank actions (car-pool, coach, LED, heating setpoint, kit swap…) by **kg CO₂ saved and KM saved**. Every price or saving is an explicit, sourced assumption.
4. Ongoing: headline numbers + limitations for slides; keep `DATA_SOURCES.md` complete (sources go on the final slide).

### B · Backend & Integration
1. `feature/club-model`: Postgres tables (club, energy_reading, trip, kit_purchase) + Alembic migration + endpoints; seed from the pack.
2. `feature/facility-distances`: OpenStreetMap facilities (`make data` again; Overpass was busy) → nearest facilities / distance between clubs (haversine) → car-pool and shared-bus suggestions.
3. `feature/analysis-api`: expose A's heating and action-plan functions as endpoints (+ tests).
4. `feature/deploy`: backend on Render, frontend on Vercel, env vars, a public URL for the jury (deploy early, then update).

### C · Frontend & Story
1. `feature/club-dashboard`: the club's own page: monthly energy chart, trips, kit, totals (uses B's endpoints).
2. `feature/action-plan-ui`: ranked action cards: "do this first: saves X kg CO₂ and Y KM a season".
3. `feature/facility-map`: map of BiH sports facilities (add `react-leaflet` in this branch); show nearby clubs to share transport or pitches.
4. Story: fill in `frontend/src/content/project.ts` + README sections; slides; 2-minute demo script; screenshots/recording as backup; check on a phone.

## Rhythm
- **Every ~2 h: 10-min sync.** What's merged, what's blocked, cut scope if behind.
- Keep PRs small (½–2 h of work). Merge into `dev` as soon as CI is green, so others build on it.
- `make sync` on your branch after anything is merged into `dev`.
- **Feature freeze ~3 h before presentation** → bug fixes, polish, rehearse twice, final PR `dev → main`.

## Definition of done (every PR)
- `make check` passes locally, CI green
- Numbers on screen show their source / assumption
- Works in light + dark mode and on a phone-width screen
- No data files, secrets or `.env` in the diff
