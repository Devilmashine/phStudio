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

    # --- Telegram Integration (Comprehensive) ---
    # Bot Configuration
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram bot token")
    TELEGRAM_CHAT_ID: str = Field(..., description="Telegram chat ID for notifications")
    TELEGRAM_WEBHOOK_URL: str = Field(default="", description="Telegram webhook URL")
    TELEGRAM_WEBHOOK_SECRET: str = Field(default="", description="Telegram webhook secret token")
    
    # API Configuration
    TELEGRAM_API_TIMEOUT: int = Field(default=30, description="Telegram API request timeout in seconds")
    TELEGRAM_CONNECTION_POOL_SIZE: int = Field(default=10, description="HTTP connection pool size")
    TELEGRAM_MAX_RETRIES: int = Field(default=3, description="Maximum retry attempts for failed messages")
    TELEGRAM_RETRY_BACKOFF_FACTOR: float = Field(default=2.0, description="Exponential backoff factor for retries")
    
    # Rate Limiting
    TELEGRAM_RATE_LIMIT_REQUESTS: int = Field(default=30, description="Max requests per window")
    TELEGRAM_RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # Queue Configuration
    TELEGRAM_QUEUE_NAME: str = Field(default="telegram_messages", description="Redis queue name for messages")
    TELEGRAM_DLQ_NAME: str = Field(default="telegram_dlq", description="Dead letter queue name")
    TELEGRAM_WORKER_CONCURRENCY: int = Field(default=5, description="Number of concurrent message workers")
    
    # Message Configuration
    TELEGRAM_MESSAGE_MAX_LENGTH: int = Field(default=4096, description="Maximum message length")
    TELEGRAM_DEFAULT_PARSE_MODE: str = Field(default="HTML", description="Default message parse mode")
    
    # Feature Flags
    TELEGRAM_ENABLE_WEBHOOKS: bool = Field(default=True, description="Enable webhook processing")
    TELEGRAM_ENABLE_QUEUE: bool = Field(default=True, description="Enable message queuing")
    TELEGRAM_ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection")
    
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
    
    # Telegram configuration validation
    def validate_telegram_config(self) -> bool:
        """Validate essential Telegram configuration"""
        if not self.TELEGRAM_BOT_TOKEN:
            return False
        if not self.TELEGRAM_CHAT_ID:
            return False
        # Validate bot token format
        if not (self.TELEGRAM_BOT_TOKEN.startswith('bot') or ':' in self.TELEGRAM_BOT_TOKEN):
            return False
        # Validate chat ID format
        if not (self.TELEGRAM_CHAT_ID.startswith('-') or self.TELEGRAM_CHAT_ID.isdigit()):
            return False
        return True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
        case_sensitive = True


from functools import lru_cache


@lru_cache()
def get_settings():
    return Settings()
