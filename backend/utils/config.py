"""
Configuration management using Pydantic settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    ENVIRONMENT: str = "development"
    
    # Gemini AI
    GEMINI_API_KEY: str
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Vercel Deployment
    VERCEL_API_TOKEN: str = ""
    
    # Security
    SECRET_KEY: str
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:3000,http://127.0.0.1:5173"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Session Management
    SESSION_TTL_HOURS: int = 24
    SESSION_CLEANUP_DAYS: int = 90
    
    # Agent Configuration
    MAX_RETRIES: int = 3
    AGENT_TIMEOUT_SECONDS: int = 300
    LLM_TEMPERATURE: float = 0.2
    
    # Quality Thresholds
    MIN_SEO_SCORE: int = 70
    MIN_ACCESSIBILITY_SCORE: int = 80
    MIN_PERFORMANCE_SCORE: int = 75
    MAX_IMPROVEMENT_CYCLES: int = 2
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
