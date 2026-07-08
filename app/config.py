from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = "development"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "cassiopeia"
    mongo_server_selection_timeout_ms: int = 2000
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_model: str = "claude-opus-4-8"
    openai_model: str = "gpt-5.1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
