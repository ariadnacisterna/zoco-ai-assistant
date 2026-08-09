from functools import lru_cache
from typing import Self

from pydantic import (
    AnyHttpUrl,
    Field,
    NonNegativeInt,
    PositiveInt,
    SecretStr,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.enums import Environment


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Environment = Field(...)

    frontend_origin: AnyHttpUrl = Field(...)

    mongodb_uri: str = Field(...)
    mongodb_database: str = Field(...)
    mongodb_timeout_ms: PositiveInt = Field(...)

    gemini_api_key: SecretStr = Field(...)
    gemini_generation_model: str = Field(...)
    gemini_embedding_model: str = Field(...)
    embedding_dimension: PositiveInt = Field(...)

    zoco_base_url: AnyHttpUrl = Field(...)
    update_interval_hours: PositiveInt = Field(...)
    max_crawl_pages: PositiveInt = Field(...)
    scraper_timeout_ms: PositiveInt = Field(...)
    chunk_size: PositiveInt = Field(...)
    chunk_overlap: NonNegativeInt = Field(...)

    retrieval_top_k: PositiveInt = Field(...)
    min_similarity: float = Field(..., ge=0.0, le=1.0)

    conversation_context_messages: PositiveInt = Field(...)
    max_message_length: PositiveInt = Field(...)

    @model_validator(mode="after")
    def validate_chunk_configuration(self) -> Self:
        """Ensure that chunk overlap is smaller than chunk size."""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be lower than CHUNK_SIZE")

        return self


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()
