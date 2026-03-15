from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    APP_NAME: str = "Smart GRH"
    DEBUG: bool = False
    DATABASE_URL: str
    FRONTEND_URL: str = "http://localhost:3000"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SUPERUSER_MATRICULE: str | None = None
    SUPERUSER_PASSWORD: str | None = None

    @field_validator("DEBUG", mode="before")
    @classmethod
    def normalize_debug_value(cls, value: bool | str) -> bool | str:
        """Accept deployment-style debug strings without crashing settings load."""
        if not isinstance(value, str):
            return value

        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "production", "prod"}:
            return False
        return value

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Normalize database URLs for the drivers installed in this project."""
        if not isinstance(value, str):
            return value

        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)

        if value.startswith("postgresql://") and "+" not in value.split("://", 1)[0]:
            return value.replace("postgresql://", "postgresql+psycopg://", 1)

        if value.startswith("mysql://"):
            return value.replace("mysql://", "mysql+pymysql://", 1)

        return value

    @field_validator("FRONTEND_URL", mode="before")
    @classmethod
    def normalize_frontend_url(cls, value: str) -> str:
        """Normalize the configured frontend origin used by CORS."""
        if not isinstance(value, str):
            return value

        normalized_origins = []
        for origin in value.split(","):
            normalized_origin = origin.strip().rstrip("/")
            if normalized_origin:
                normalized_origins.append(normalized_origin)

        return ",".join(normalized_origins)

    @property
    def cors_allowed_origins(self) -> list[str]:
        """Return the explicit CORS allowlist for local and deployed frontends."""
        origins = [
            "http://localhost:3000",
            "http://localhost:5173",
        ]

        origins.extend(
            origin
            for origin in self.FRONTEND_URL.split(",")
            if origin
        )

        return list(dict.fromkeys(origins))

    # Use the Pydantic v2 settings configuration API.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
