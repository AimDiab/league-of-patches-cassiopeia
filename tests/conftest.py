import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.db.mongo import get_client
from app.main import app


@pytest.fixture(autouse=True)
def fast_mongo_timeout(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "200")
    get_settings.cache_clear()
    get_client.cache_clear()
    yield
    get_settings.cache_clear()
    get_client.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
