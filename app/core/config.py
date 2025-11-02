from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings and configuration."""

    # Project
    PROJECT_NAME: str = "Lecture MCP Server"
    VERSION: str = "0.1.0"
    API_STR: str = "/api"
    DESCRIPTION: str = "MCP Server for PDF lecture processing with Gemini AI"

    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production

    # Gemini API
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Processing
    MAX_CHUNK_SIZE: int = 2000
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    WORKERS: int = 1

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
