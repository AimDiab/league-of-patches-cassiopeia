import asyncio
import json
from dataclasses import dataclass
from typing import Any

import pytest

from app.llm.anthropic_provider import AnthropicProvider
from app.llm.exceptions import LLMClassificationError
from app.llm.schemas import PatchNoteClassification


@dataclass
class FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class FakeMessage:
    content: list[Any]
    stop_reason: str = "end_turn"


class FakeStream:
    def __init__(self, message: FakeMessage):
        self._message = message

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def get_final_message(self) -> FakeMessage:
        return self._message


class FakeMessages:
    def __init__(self, message: FakeMessage):
        self._message = message

    def stream(self, **kwargs):
        return FakeStream(self._message)


class FakeClient:
    def __init__(self, message: FakeMessage):
        self.messages = FakeMessages(message)


def _provider_with_response(text: str) -> AnthropicProvider:
    provider = AnthropicProvider(api_key="test-key", model="claude-opus-4-8")
    provider._client = FakeClient(FakeMessage(content=[FakeTextBlock(text=text)]))
    return provider


def test_fetch_and_classify_returns_valid_classification():
    payload = {
        "patch_version": "14.3",
        "source_url": "https://example.com/patch-14-3",
        "changes": [
            {
                "entity_name": "Ahri",
                "entity_type": "champion",
                "change_type": "nerf",
                "summary": "Reduced Q damage.",
            }
        ],
        "overall_summary": "Ahri nerfed.",
    }
    provider = _provider_with_response(json.dumps(payload))

    result = asyncio.run(provider.fetch_and_classify("https://example.com/patch-14-3"))

    assert isinstance(result, PatchNoteClassification)
    assert result.patch_version == "14.3"
    assert result.changes[0].entity_name == "Ahri"


def test_fetch_and_classify_raises_on_malformed_json():
    provider = _provider_with_response("not valid json")

    with pytest.raises(LLMClassificationError):
        asyncio.run(provider.fetch_and_classify("https://example.com/patch-14-3"))
