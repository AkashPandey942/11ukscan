"""
Application configuration module.

Loads all settings from environment variables / .env file using
Pydantic BaseSettings. This is the single source of truth for
all configuration values across the application.

Never import raw os.environ in business logic — always inject
Settings via FastAPI dependency injection.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings.

    All values are read from environment variables or a .env file.
    Provides typed, validated access to configuration throughout
    the application.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Application metadata
    # ------------------------------------------------------------------ #
    APP_NAME: str = Field(default="BankScan", description="Human-readable application name")
    APP_VERSION: str = Field(default="1.0.0", description="Semantic version string")
    DEBUG: bool = Field(default=False, description="Enable debug mode (never True in production)")

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    LOG_LEVEL: str = Field(default="INFO", description="Python logging level: DEBUG|INFO|WARNING|ERROR")

    # ------------------------------------------------------------------ #
    # Upload constraints
    # ------------------------------------------------------------------ #
    MAX_UPLOAD_SIZE_MB: int = Field(default=50, description="Maximum allowed PDF upload size in megabytes", gt=0)
    MAX_PDF_PAGES: int = Field(default=60, description="Maximum number of pages allowed in uploaded PDF", gt=0)

    # ------------------------------------------------------------------ #
    # File system paths
    # ------------------------------------------------------------------ #
    UPLOAD_DIR: Path = Field(default=Path("uploads"), description="Directory for temporary PDF storage")
    OUTPUT_DIR: Path = Field(default=Path("outputs"), description="Directory for generated CSV/Excel files")

    # ------------------------------------------------------------------ #
    # CORS
    # ------------------------------------------------------------------ #
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="List of allowed CORS origins",
    )

    # ------------------------------------------------------------------ #
    # Future — MongoDB
    # ------------------------------------------------------------------ #
    MONGO_URI: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URI")
    MONGO_DB_NAME: str = Field(default="bankscan", description="MongoDB database name")

    # ------------------------------------------------------------------ #
    # Future — JWT Authentication
    # ------------------------------------------------------------------ #
    JWT_SECRET: str = Field(default="change-me-in-production", description="JWT signing secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_EXPIRE_MINUTES: int = Field(default=60, description="JWT token expiry in minutes", gt=0)

    # ------------------------------------------------------------------ #
    # Admin panel
    # ------------------------------------------------------------------ #
    ADMIN_API_TOKEN: str = Field(
        default="change-me-in-production",
        description="Shared-secret token required in the X-Admin-Token header for /api/v1/admin/* routes",
    )

    # ------------------------------------------------------------------ #
    # Computed / derived
    # ------------------------------------------------------------------ #
    @property
    def max_upload_size_bytes(self) -> int:
        """Return MAX_UPLOAD_SIZE_MB expressed as bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure LOG_LEVEL is a recognised Python logging level."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}, got '{v}'")
        return upper

    def ensure_directories(self) -> None:
        """
        Create upload and output directories if they do not exist.

        Call once at application startup (in main.py lifespan handler).
        """
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton Settings instance.

    Using @lru_cache ensures .env is only parsed once per process.
    Inject this via FastAPI's Depends() to keep endpoints testable.

    Returns:
        Settings: The application settings singleton.
    """
    return Settings()
