import pytest

from app.llm.dependencies import get_anthropic_provider
from app.llm.exceptions import LLMClassificationError, LLMFetchError
from app.llm.schemas import PatchNoteClassification
from app.main import app

VALID_CLASSIFICATION = PatchNoteClassification(
    patch_version="14.3",
    source_url="https://example.com/patch-14-3",
    changes=[
        {
            "entity_name": "Ahri",
            "entity_type": "champion",
            "change_type": "nerf",
            "summary": "Reduced Q damage.",
        }
    ],
    overall_summary="Ahri nerfed.",
)


class FakeProvider:
    def __init__(self, result=None, error=None):
        self._result = result
        self._error = error

    async def fetch_and_classify(self, url: str) -> PatchNoteClassification:
        if self._error is not None:
            raise self._error
        return self._result


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.pop(get_anthropic_provider, None)


def test_classify_returns_valid_classification(client):
    app.dependency_overrides[get_anthropic_provider] = lambda: FakeProvider(
        result=VALID_CLASSIFICATION
    )

    response = client.post("/classify", json={"url": "https://example.com/patch-14-3"})

    assert response.status_code == 200
    assert response.json()["patch_version"] == "14.3"
    assert response.json()["changes"][0]["entity_name"] == "Ahri"


def test_classify_maps_fetch_error_to_502(client):
    app.dependency_overrides[get_anthropic_provider] = lambda: FakeProvider(
        error=LLMFetchError("could not fetch url")
    )

    response = client.post("/classify", json={"url": "https://example.com/patch-14-3"})

    assert response.status_code == 502


def test_classify_maps_classification_error_to_422(client):
    app.dependency_overrides[get_anthropic_provider] = lambda: FakeProvider(
        error=LLMClassificationError("malformed response")
    )

    response = client.post("/classify", json={"url": "https://example.com/patch-14-3"})

    assert response.status_code == 422


def test_classify_rejects_invalid_url(client):
    response = client.post("/classify", json={"url": "not-a-url"})

    assert response.status_code == 422
