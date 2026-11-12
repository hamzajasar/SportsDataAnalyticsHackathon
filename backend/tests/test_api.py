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


def test_sample_stats():
    r = client.get("/api/sample/stats")
    assert r.status_code == 200
    assert len(r.json()["points"]) == 10


def test_datasets_disabled_in_production():
    from app.core.config import Settings

    assert Settings(environment="development").datasets_enabled is True
    assert Settings(environment="production").datasets_enabled is False
    assert Settings(environment="production", expose_datasets=True).datasets_enabled is True
