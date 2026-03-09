from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    APP_NAME: str = "Smart GRH"
    DEBUG: bool = False
    DATABASE_URL: str
    CREATE_TABLES_ON_STARTUP: bool = False

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Use the Pydantic v2 settings configuration API.
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
