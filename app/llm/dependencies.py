from functools import lru_cache

from app.config import get_settings
from app.llm.anthropic_provider import AnthropicProvider


@lru_cache
def get_anthropic_provider() -> AnthropicProvider:
    settings = get_settings()
    return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_model)
