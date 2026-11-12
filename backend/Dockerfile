# Build from the REPO ROOT so the shared data/clean/ files are included:
#   docker build -f backend/Dockerfile .
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev
COPY backend/app ./app
COPY backend/migrations ./migrations
COPY backend/alembic.ini ./
COPY data/clean ./data/clean
ENV PATH="/app/.venv/bin:$PATH" \
    DATA_DIR=/app/data
RUN useradd --create-home --uid 1001 app && chown -R app /app
USER app
EXPOSE 8000
# Render sets $PORT; default 8000 locally
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
