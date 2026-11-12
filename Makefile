.PHONY: help setup feature sync finish deps dev db db-stop migrate migration data reference profile backend frontend notebook gen-api lint format test check clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Install all dependencies + git hooks (run once after cloning)
	@test -f .env || cp .env.example .env
	cd backend && uv sync
	cd frontend && npm install
	uv run --project backend pre-commit install
	uv run --project backend nbstripout --install

feature: ## Start a feature branch from latest dev: make feature name=trip-calculator
	@test -n "$(name)" || (echo 'usage: make feature name=<short-name>' && exit 1)
	git fetch origin
	git switch -c feature/$(name) origin/dev
	@echo "On feature/$(name). Push with: git push -u origin feature/$(name)"

sync: ## Update current feature branch with latest dev (merge)
	git fetch origin
	git merge origin/dev

finish: ## Test this feature branch; if it passes, merge it into dev and push (no PRs)
	@b=$$(git branch --show-current); \
	case "$$b" in dev|main) echo "Run this from a feature branch, not $$b"; exit 1;; esac; \
	test -z "$$(git status --porcelain)" || { echo "Commit or stash your changes first"; exit 1; }; \
	git fetch origin && git merge --no-edit origin/dev && \
	$(MAKE) check && \
	git push -u origin "$$b" && \
	git switch dev && git merge --ff-only origin/dev && git merge --no-edit "$$b" && \
	git push origin dev && git switch "$$b" && \
	echo "OK: $$b merged into dev and pushed"

db: ## Start Postgres in Docker
	docker compose up -d --wait db

db-stop: ## Stop Postgres
	docker compose stop db

migrate: ## Apply DB migrations (alembic upgrade head)
	cd backend && uv run alembic upgrade head

migration: ## Create migration from model changes: make migration m="add teams table"
	@test -n "$(m)" || (echo 'usage: make migration m="message"' && exit 1)
	cd backend && uv run alembic revision --autogenerate -m "$(m)"

data: ## Download all open datasets: data/raw (ignored). FORCE=1 to refresh
	cd backend && FORCE=$(FORCE) uv run python -m scripts.fetch_open_data

reference: ## Rebuild ALL committed reference tables in backend/app/reference
	cd backend && uv run python -m scripts.build_reference

profile: ## Profile all datasets in data/raw -> data/processed/_profile.md
	cd backend && uv run python -m scripts.profile_data

backend: ## Run FastAPI with reload on :8000 (docs at /docs)
	cd backend && uv run fastapi dev app/main.py --port 8000

frontend: ## Run Vite dev server on :5173
	cd frontend && npm run dev

deps: ## Install frontend packages if package-lock.json changed since the last install
	@cd frontend && if [ ! -f node_modules/.package-lock.json ] || [ package-lock.json -nt node_modules/.package-lock.json ]; then \
		echo "Frontend packages changed after a pull: installing (npm ci)…"; npm ci --no-audit --no-fund; \
	fi

dev: deps ## Start backend + frontend together (no database needed; Ctrl+C stops all)
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
	cd backend && uv run pytest -q --cov=app --cov-fail-under=85
	cd frontend && npm test

check: lint test ## Lint + test + frontend build (same as CI)
	cd frontend && npm run build

clean: ## Remove caches and build output
	rm -rf frontend/dist backend/.pytest_cache backend/.ruff_cache
