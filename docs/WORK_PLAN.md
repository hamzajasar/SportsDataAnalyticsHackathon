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

## Target app (agreed)
Summary bar **"Save X KM/yr · Y t CO₂/yr · fee −Z KM/child"** + top 3 actions ranked by payback ·
tabs **Energy | Travel | Share | Affordability | Assumptions & Sources** · printable board report ·
opens with the sample Sarajevo club, every assumption editable.

**Already in `dev`:** Footprint page (grid chart + electricity / trip / kit calculators), Data explorer,
How-it-works page; API: `/api/sustainability/*`, `/api/club/sample`, `/api/club/assumptions`,
`/api/venues` (3,705 BiH venues, distance filter), `/api/sources`.

## Backlog (in priority order per lane)

### A · Data & Analysis
1. `feature/pack-ingest`: organisers' pack → `data/raw/pack/` → clean into `data/clean/` (replaces the placeholder sample club), document every cleaning step.
2. `feature/energy-model`: yearly kWh by use (floodlights / heating / hall); heating spread by month with Sarajevo temperature (heating degrees); solar yield from PVGIS. Pure functions in `services/` + tests.
3. `feature/savings-model`: per upgrade (LED, solar, insulation, car-sharing) → KM saved, CO₂ saved, **payback = cost ÷ yearly saving**, **fee drop per child = total saving ÷ children**. Every price is a sourced assumption (`cost_assumptions.csv` — verify prices!).
4. Ongoing: headline numbers + limitations for slides; keep `DATA_SOURCES.md` complete.

### B · Backend & Integration
1. `feature/club-api`: `POST /api/club/footprint` (club profile in → totals by tab out) and `POST /api/club/actions` (ranked actions) — ship the response shape first with example numbers, `make gen-api`, then plug in A's functions.
2. `feature/share-api`: nearby venues/clubs for pitch or minibus sharing, built on `/api/venues` (distance already implemented).
3. `feature/club-model` (only if needed): save/load club profiles in Postgres (Alembic migration).
4. Keep `make check` + CI green on `dev`; help C wire endpoints.

### C · Frontend & Story
1. `feature/summary-bar`: the headline bar + top-3 actions (uses `/api/club/*`).
2. `feature/tabs`: Energy | Travel | Share | Affordability | Assumptions & Sources (reuse Footprint calculators; Sources tab from `/api/sources`).
3. `feature/share-map`: map of BiH venues (`react-leaflet` + OSM tiles) with nearby clubs.
4. `feature/board-report`: printable one-page summary (print CSS).
5. Story: `content/project.ts` + README, slides, 2-minute demo script, backup recording.

## Rhythm
- **Syncs at 13:30 and 15:15. Feature lock at 15:15** → then only bug fixes, polish, rehearsal.
- Small branches (½–2 h). `make finish` merges into `dev` when tests pass, so others build on it.
- `make sync` on your branch after anything is merged into `dev`.
- At the very end: `dev → main` (only when the team says so).

## Definition of done (every branch)
- `make check` passes locally (`make finish` enforces it), CI green
- Numbers on screen show their source / assumption
- Works in light + dark mode and on a phone-width screen
- No data files, secrets or `.env` in the diff
