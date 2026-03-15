from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    APP_NAME: str = "Smart GRH"
    DEBUG: bool = False
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SUPERUSER_MATRICULE: str | None = None
    SUPERUSER_PASSWORD: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Normalize database URLs for the drivers installed in this project."""
        if not isinstance(value, str):
            return value

        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg2://", 1)

        if value.startswith("postgresql://") and "+" not in value.split("://", 1)[0]:
            return value.replace("postgresql://", "postgresql+psycopg2://", 1)

        if value.startswith("mysql://"):
            return value.replace("mysql://", "mysql+pymysql://", 1)

        return value

    # Use the Pydantic v2 settings configuration API.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
