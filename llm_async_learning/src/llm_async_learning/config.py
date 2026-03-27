from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    openai_api_key: SecretStr = Field(alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_max_concurrency: int = Field(default=5, alias="OPENAI_MAX_CONCURRENCY", ge=1)
    openai_timeout_seconds: int = Field(default=30, alias="OPENAI_TIMEOUT_SECONDS", ge=1)
    openai_retry_attempts: int = Field(default=3, alias="OPENAI_RETRY_ATTEMPTS", ge=1)
    openai_retry_min_seconds: int = Field(default=1, alias="OPENAI_RETRY_MIN_SECONDS", ge=0)
    openai_retry_max_seconds: int = Field(default=8, alias="OPENAI_RETRY_MAX_SECONDS", ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


def load_settings() -> AppSettings:
    return AppSettings()
