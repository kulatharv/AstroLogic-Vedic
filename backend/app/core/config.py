from dataclasses import dataclass
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[3]
#DEFAULT_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/astrologicai"
DEFAULT_DATABASE_URL = "sqlite:///./astrologic.db"

def _csv_env(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AstroLogicAI")
    environment: str = os.getenv("ENVIRONMENT", os.getenv("ENV", "development"))
    debug: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"}

    database_url: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    database_pool_recycle_seconds: int = int(os.getenv("DATABASE_POOL_RECYCLE_SECONDS", "1800"))
    secret_key: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    session_secret_key: str = os.getenv(
        "SESSION_SECRET_KEY",
        os.getenv("SECRET_KEY", "change-this-session-secret"),
    )
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        os.getenv("SECRET_KEY", "change-this-jwt-secret"),
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    cors_origins: tuple[str, ...] = tuple(_csv_env("CORS_ORIGINS", "*"))
    api_ninjas_key: str | None = os.getenv("API_NINJAS_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
