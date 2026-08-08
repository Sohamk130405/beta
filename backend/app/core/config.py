from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="GeoAttend API", validation_alias="APP_NAME")
    environment: Literal["development", "test", "production"] = Field(
        default="development",
        validation_alias="ENVIRONMENT",
    )
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/geoattend",
        validation_alias="DATABASE_URL",
    )
    frontend_url: str = Field(
        default="http://localhost:3000",
        validation_alias="FRONTEND_URL",
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        validation_alias="CORS_ORIGINS",
    )
    google_client_id: str | None = Field(
        default=None,
        validation_alias="GOOGLE_CLIENT_ID",
    )
    google_client_secret: SecretStr | None = Field(
        default=None,
        validation_alias="GOOGLE_CLIENT_SECRET",
    )
    jwt_secret: SecretStr | None = Field(default=None, validation_alias="JWT_SECRET")
    arcjet_key: SecretStr | None = Field(default=None, validation_alias="ARCJET_KEY")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
