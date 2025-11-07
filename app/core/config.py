from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration."""

    # Project
    PROJECT_NAME: str = "Lecture MCP Server"
    VERSION: str = "0.2.0"
    DESCRIPTION: str = "MCP Server for PDF lecture processing with Gemini AI"

    # Environment
    ENVIRONMENT: str = "development"

    # Gemini API
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 8192
    GEMINI_TIMEOUT: int = 60  # seconds

    # Rate Limiting
    GEMINI_MAX_REQUESTS_PER_MINUTE: int = 60
    GEMINI_MAX_TOKENS_PER_MINUTE: int = 32000

    # Processing
    MAX_CHUNK_SIZE: int = 2000
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

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
