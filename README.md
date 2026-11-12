# SportsDataAnalyticsHackathon

> **Topic:** _TBD_ · **Team:** _TBD_ · **Live demo:** _TBD_

<!-- Sections mirror the judging criteria in docs/JUDGING_CRITERIA.md. Keep each short and concrete. -->

## The problem (relevance)
_Who has this problem (coach, club, youth org, player)? What decision do we help them make? One-sentence pitch._

## Data & methodology (data quality and analytical soundness)
- **Data:** _source, size, time span, key tables_
- **Cleaning:** _what we fixed / removed and why_
- **Method:** _approach, and why it fits the question_
- **Validation:** _baseline vs our result, how we tested (e.g. time-based split)_
- **Limitations:** _what the data can't tell us_

## What we built (technical execution)
_Screenshots + live link. Short description of the main features._

## What's new (innovation and creativity)
_The non-obvious insight or the feature nobody else has._

## Impact & inclusion (feasibility, impact and inclusion)
_Who benefits, how it would be adopted, cost to run, how it includes youth / underrepresented groups / small clubs._

## Team
_Names and roles._

---

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | React 19 · TypeScript · Vite · Tailwind CSS v4 · shadcn/ui · TanStack Query · React Router · Recharts · ECharts |
| Backend | FastAPI · Pydantic · SQLAlchemy · Alembic · pandas · scikit-learn · xgboost · statsmodels · DuckDB |
| Database | PostgreSQL 17 (Docker) |
| Tooling | uv · npm · ruff · oxlint · Prettier · pytest · Vitest · pre-commit · nbstripout · GitHub Actions |
| Deploy | Vercel (frontend) · Render (backend, `render.yaml`) |

## Getting started

Prerequisites: [uv](https://docs.astral.sh/uv/), Node 22+, Docker, make.

```bash
make setup   # install deps + git hooks (once)
make dev     # Postgres + API (:8000) + web (:5173)
```

- App: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs

Run `make help` for all commands.

### Working with the provided datasets

```bash
# put files (csv, parquet, json, xlsx) in data/raw/ — they are git-ignored
make profile        # rows, columns, types, missing %, likely keys, probable joins
                    # -> data/processed/_profile.md
make seed           # optional: load them into Postgres as raw_* tables
make sample-data    # fake sports data to try the tooling (make clean-sample removes it)
```

The **Data** page in the app (`/data`) browses any file in `data/raw/` (rows, sorting, column stats).
In notebooks / backend code: `from app.services.datasets import load_df` → `load_df("file.csv")`.

See [docs/HACKATHON_PLAYBOOK.md](docs/HACKATHON_PLAYBOOK.md) for the plan for the day.

## Project structure

```
backend/
  app/
    api/routes/     # FastAPI endpoints (one file per feature)
    services/       # analytics / ML logic; datasets.py = generic data access
    schemas/        # Pydantic request/response schemas
    models/         # SQLAlchemy ORM models (DB tables)
    db/             # SQLAlchemy engine/session
    core/config.py  # settings from .env
  migrations/       # Alembic DB migrations
  scripts/          # profile_data, seed_db, make_sample_data, export_openapi
  tests/
frontend/
  src/
    api/            # generated schema.d.ts + typed client + React Query hooks
    pages/          # one component per route
    components/     # common/ (DataTable, StatCard, PageHeader, QueryState, ErrorBoundary),
                    # charts/, layout/, ui/ (shadcn primitives)
    lib/            # format, table, errors helpers
    test/           # Vitest setup + render helpers
notebooks/          # 01_exploration, 02_baseline_model (outputs auto-stripped on commit)
models/             # saved models (git-ignored)
data/raw|processed/ # git-ignored datasets
docs/               # brief, judging criteria, presentation assets
```

## Adding a feature end-to-end

1. Logic in `backend/app/services/<feature>.py`
2. Response schema in `backend/app/schemas/` (and ORM model in `app/models/` + `make migration m="..."` if it needs a table)
3. Endpoint in `backend/app/api/routes/<feature>.py` (set `operation_id`), register it in `api/router.py`
4. `make gen-api` → regenerates typed frontend client
5. Hook in `frontend/src/api/queries.ts`, page in `frontend/src/pages/`, route in `App.tsx`

## Team workflow

- Branch per feature: `feat/<name>`, PR into `main`, keep PRs small.
- Never commit data files or `.env`; put download steps in `backend/scripts/`.
- Notebooks: prefix with a number (`02_model.ipynb`); move reusable code into `services/`.
