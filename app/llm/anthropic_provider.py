import json
from typing import Any

import anthropic
from pydantic import ValidationError

from app.llm.base import LLMProvider
from app.llm.exceptions import LLMClassificationError, LLMFetchError
from app.llm.schemas import PatchNoteClassification

_MAX_PAUSE_TURN_RETRIES = 3


def _require_no_additional_properties(schema: dict[str, Any]) -> dict[str, Any]:
    if schema.get("type") == "object":
        schema.setdefault("additionalProperties", False)
    for value in schema.get("properties", {}).values():
        _require_no_additional_properties(value)
    for value in schema.get("$defs", {}).values():
        _require_no_additional_properties(value)
    if isinstance(schema.get("items"), dict):
        _require_no_additional_properties(schema["items"])
    return schema


class AnthropicProvider(LLMProvider):
    """LLMProvider backed by the Anthropic Messages API."""

    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def fetch_and_classify(self, url: str) -> PatchNoteClassification:
        system = self.build_system_prompt()
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": self.build_user_prompt(url)}
        ]

        response = await self._create_message(system, messages)

        retries = 0
        while response.stop_reason == "pause_turn":
            if retries >= _MAX_PAUSE_TURN_RETRIES:
                raise LLMFetchError(
                    f"web_fetch did not complete after {_MAX_PAUSE_TURN_RETRIES} pause_turn retries"
                )
            messages.append({"role": "assistant", "content": response.content})
            response = await self._create_message(system, messages)
            retries += 1

        if response.stop_reason == "refusal":
            raise LLMClassificationError("Anthropic model refused to classify the patch notes")

        for block in response.content:
            if block.type == "web_fetch_tool_result" and getattr(block.content, "error_code", None):
                raise LLMFetchError(f"web_fetch failed: {block.content.error_code}")

        text = next((block.text for block in response.content if block.type == "text"), None)
        if text is None:
            raise LLMClassificationError("Anthropic response contained no text block to parse")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMClassificationError(f"Anthropic response was not valid JSON: {exc}") from exc

        try:
            return PatchNoteClassification.model_validate(data)
        except ValidationError as exc:
            raise LLMClassificationError(
                f"Anthropic response did not match PatchNoteClassification: {exc}"
            ) from exc

    async def _create_message(self, system: str, messages: list[dict[str, Any]]):
        schema = _require_no_additional_properties(PatchNoteClassification.model_json_schema())
        try:
            async with self._client.messages.stream(
                model=self.model,
                max_tokens=16000,
                system=system,
                tools=[{"type": "web_fetch_20260209", "name": "web_fetch"}],
                output_config={"format": {"type": "json_schema", "schema": schema}},
                messages=messages,
            ) as stream:
                return await stream.get_final_message()
        except (anthropic.APIConnectionError, anthropic.APIStatusError) as exc:
            raise LLMFetchError(f"Anthropic request failed: {exc}") from exc
