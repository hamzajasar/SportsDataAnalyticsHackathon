import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.skipif(not os.getenv("REQUIRE_DB"), reason="set REQUIRE_DB=1 to check DB")
def test_health_database_connected():
    assert client.get("/api/health").json()["database"] is True


def test_hosted_database_urls_get_psycopg_driver():
    from app.core.config import Settings

    for raw in ("postgres://u:p@h:5432/db", "postgresql://u:p@h:5432/db"):
        assert Settings(database_url=raw).database_url == "postgresql+psycopg://u:p@h:5432/db"
    local = "postgresql+psycopg://u:p@localhost:5432/db"
    assert Settings(database_url=local).database_url == local
