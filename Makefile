.PHONY: help setup dev db db-stop migrate migration profile seed sample-data clean-sample backend frontend notebook gen-api lint format test check clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Install all dependencies + git hooks (run once after cloning)
	@test -f .env || cp .env.example .env
	cd backend && uv sync
	cd frontend && npm install
	uv run --project backend pre-commit install
	uv run --project backend nbstripout --install

db: ## Start Postgres in Docker
	docker compose up -d --wait db

db-stop: ## Stop Postgres
	docker compose stop db

migrate: ## Apply DB migrations (alembic upgrade head)
	cd backend && uv run alembic upgrade head

migration: ## Create migration from model changes: make migration m="add teams table"
	@test -n "$(m)" || (echo 'usage: make migration m="message"' && exit 1)
	cd backend && uv run alembic revision --autogenerate -m "$(m)"

profile: ## Profile all datasets in data/raw -> data/processed/_profile.md
	cd backend && uv run python -m scripts.profile_data

seed: db ## Load data/raw files into Postgres as raw_* tables (one file: make seed f="x.csv")
	cd backend && uv run python -m scripts.seed_db $(f)

sample-data: ## Generate fake sports data in data/raw/_sample to try the tooling
	cd backend && uv run python -m scripts.make_sample_data

clean-sample: ## Remove the fake sample data
	rm -rf data/raw/_sample

backend: ## Run FastAPI with reload on :8000 (docs at /docs)
	cd backend && uv run fastapi dev app/main.py --port 8000

frontend: ## Run Vite dev server on :5173
	cd frontend && npm run dev

dev: db migrate ## Start DB + backend + frontend together (Ctrl+C stops all)
	@trap 'kill 0' INT TERM EXIT; \
	(cd backend && uv run fastapi dev app/main.py --port 8000) & \
	(cd frontend && npm run dev) & \
	wait

notebook: ## Open JupyterLab (backend `app` package importable)
	cd backend && PYTHONPATH=$(CURDIR)/backend uv run jupyter lab --notebook-dir=$(CURDIR)/notebooks

gen-api: ## Regenerate the TS API client from FastAPI's OpenAPI schema
	cd backend && uv run python -m scripts.export_openapi
	cd frontend && npm run gen:api

lint: ## Lint backend + frontend
	cd backend && uv run ruff check . ../notebooks && uv run ruff format --check . ../notebooks
	cd frontend && npm run lint && npm run format:check

format: ## Auto-format backend + frontend
	cd backend && uv run ruff check --fix . ../notebooks && uv run ruff format . ../notebooks
	cd frontend && npm run format

test: ## Run backend + frontend tests
	cd backend && uv run pytest -q
	cd frontend && npm test

check: lint test ## Lint + test + frontend build (same as CI)
	cd frontend && npm run build

clean: ## Remove caches and build output
	rm -rf frontend/dist backend/.pytest_cache backend/.ruff_cache
