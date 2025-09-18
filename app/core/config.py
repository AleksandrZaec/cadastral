from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Typed settings loaded from environment variables."""

    MODE: str

    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    EXTERNAL_SERVICE_URL: str

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
    LOG_NAME: str = "app"

    @property
    def DB_URL(self) -> str:
        """Build the async PostgreSQL DSN string."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
