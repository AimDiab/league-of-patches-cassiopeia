from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = "development"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "cassiopeia"
    mongo_server_selection_timeout_ms: int = 2000


@lru_cache
def get_settings() -> Settings:
    return Settings()
