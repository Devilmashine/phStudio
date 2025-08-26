from pydantic_settings import BaseSettings
from typing import List
from pydantic import computed_field, Field
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # --- Основные настройки ---
    ENV: str = Field(default="development", description="Environment: development, testing, production")
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    
    # PostgreSQL connection pool settings
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_POOL_MAX_OVERFLOW: int = Field(default=30, description="Maximum overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Connection timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Connection recycle time in seconds")
    
    # Test database settings
    TEST_DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/phstudio_test",
        description="Test database URL"
    )

    # --- Безопасность ---
    SECRET_KEY: str = Field(..., description="JWT secret key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, description="Access token expiration in minutes")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=10080, description="Refresh token expiration in minutes (7 days)")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    
    # Password security
    PASSWORD_MIN_LENGTH: int = Field(default=8, description="Minimum password length")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, description="Require uppercase in password")
    PASSWORD_REQUIRE_NUMBERS: bool = Field(default=True, description="Require numbers in password")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, description="Require special characters in password")
    
    # Security settings
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, description="Maximum failed login attempts")
    LOCKOUT_DURATION_MINUTES: int = Field(default=30, description="Account lockout duration")
    
    # Rate limiting (cost-effective in-memory)
    RATE_LIMIT_PER_MINUTE: int = Field(default=120, description="API requests per minute per IP")
    RATE_LIMIT_BURST: int = Field(default=200, description="Burst limit for rate limiting")

    # --- CORS ---
    CORS_ORIGINS_STR: str = Field(default="", description="Comma-separated CORS origins")

    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if not self.CORS_ORIGINS_STR:
            return ["http://localhost:3000", "http://localhost:5173"]
        return [i.strip() for i in self.CORS_ORIGINS_STR.split(",") if i.strip()]

    # --- Интеграции ---
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram bot token")
    TELEGRAM_CHAT_ID: str = Field(..., description="Telegram chat ID")
    
    # --- Redis для кэширования ---
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis URL for caching")
    
    # --- Logging ---
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    @computed_field
    @property
    def IS_TESTING(self) -> bool:
        return self.ENV == "testing"
    
    @computed_field
    @property
    def IS_PRODUCTION(self) -> bool:
        return self.ENV == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
        case_sensitive = True


from functools import lru_cache


@lru_cache()
def get_settings():
    return Settings()
