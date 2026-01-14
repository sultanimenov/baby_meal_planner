"""Application configuration using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str
    postgres_user: str = "mealplanner"
    postgres_password: str = "mealplanner"
    postgres_db: str = "mealplanner"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Application
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_url: str = "http://localhost:8000"
    environment: str = "development"
    debug: bool = True

    # Frontend
    frontend_url: str = "http://localhost:3000"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    cors_origins_production: str = ""  # Comma-separated list for production

    # Authentication
    secret_key: str
    jwt_secret: str | None = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Email (for password reset)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None

    # OpenAI
    openai_api_key: str
    # Model names used by planner (override via env without code changes)
    # Examples: "gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano", "o3-mini"
    openai_model: str = "gpt-5-mini"
    openai_repair_model: str = "gpt-5-mini"
    openai_temperature: float = 0.7
    openai_repair_temperature: float = 0.3

    # LangSmith (optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "baby-meal-planner"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url_async(self) -> str:
        """Get async database URL."""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def allowed_origins(self) -> list[str]:
        """Get CORS allowed origins based on environment."""
        if self.is_production and self.cors_origins_production:
            return [o.strip() for o in self.cors_origins_production.split(",") if o.strip()]
        return self.cors_origins


settings = Settings()

