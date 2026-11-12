# SportsDataAnalyticsHackathon

> **Topic:** 06 · The Sustainable Sports Club — _How can community clubs use data to cut energy use, travel emissions or equipment waste?_ (see [docs/TOPIC.md](docs/TOPIC.md)) · **Team:** _TBD_ · **Live demo:** _TBD_

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
| Frontend | React 19 · TypeScript · Vite · Tailwind CSS v4 · shadcn/ui · TanStack Query · React Router · Recharts |
| Backend | FastAPI · Pydantic · SQLAlchemy · Alembic · pandas · scikit-learn · statsmodels · DuckDB |
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
make data           # download the open datasets for our topic (see docs/DATA_SOURCES.md)
# organisers' synthetic pack -> data/raw/pack/  (git-ignored)
make profile        # rows, columns, types, missing %, likely keys, probable joins
                    # -> data/processed/_profile.md
make seed           # optional: load them into Postgres as raw_* tables
```

The **Data** page in the app (`/data`) browses any file in `data/raw/` (rows, sorting, column stats).
In notebooks / backend code: `from app.services.datasets import load_df` → `load_df("file.csv")`.

Who does what: [docs/WORK_PLAN.md](docs/WORK_PLAN.md). Plan for the day: [docs/HACKATHON_PLAYBOOK.md](docs/HACKATHON_PLAYBOOK.md).

## Project structure

```
backend/
  app/
    api/routes/     # FastAPI endpoints (one file per feature)
    services/       # logic: emissions.py (Topic 6 calculations), datasets.py (generic data access)
    reference/      # small committed reference tables (emission factors, grid intensity) — make reference
    schemas/        # Pydantic request/response schemas
    models/         # SQLAlchemy ORM models (DB tables)
    db/             # SQLAlchemy engine/session
    core/config.py  # settings from .env
  migrations/       # Alembic DB migrations
  scripts/          # fetch_open_data, build_reference, profile_data, seed_db, export_openapi
  tests/
frontend/
  src/
    api/            # generated schema.d.ts + typed client + React Query hooks
    pages/          # one component per route
    components/     # common/ (DataTable, StatCard, PageHeader, QueryState, ErrorBoundary),
                    # layout/, ui/ (shadcn primitives)
    lib/            # format, table, errors helpers
    test/           # Vitest setup + render helpers
notebooks/          # 01_exploration (outputs auto-stripped on commit)
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

```
main  ─────────────────────────────────────────────●  (final release only)
                                                  ↑ at the very end
dev   ──●──────────●──────────●───────────────────●
         \        ↑ \        ↑
          feature/a   feature/b      (one branch per feature, merged when tests pass)
```

1. `make feature name=<short-name>` → creates `feature/<short-name>` from the latest `dev`
2. Work and commit on that branch (`git push -u origin feature/<short-name>` any time; CI runs on every push)
3. `make finish` → merges the latest `dev` in, runs `make check`, and **only if it passes** merges your
   branch into `dev` and pushes. No pull requests.
4. **Never commit or push to `main`.** It only gets `dev` at the very end
   (a local hook blocks commits on `main`).

Other rules: never commit data files or `.env`; notebooks are numbered (`02_model.ipynb`) and reusable
code moves into `backend/app/services/`.
