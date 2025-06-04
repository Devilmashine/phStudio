from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os

class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "development")
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.db")))
    SECRET_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    GOOGLE_CALENDAR_ID: str
    GOOGLE_CALENDAR_API_KEY: str
    GOOGLE_CLIENT_EMAIL: str
    GOOGLE_PRIVATE_KEY: str
    SERVICE_ACCOUNT_FILE: str = os.getenv("SERVICE_ACCOUNT_FILE", "backend/app/config/service_account.json")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 43200))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    @field_validator("*", mode="before")
    @classmethod
    def check_not_empty(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} не может быть пустым")
        return v

    model_config = {
        "env_file": f".env.{os.getenv('ENV', 'development')}",
        "case_sensitive": True,
        "extra": "allow"
    }

try:
    settings = Settings()
except Exception as e:
    print(f"Ошибка загрузки конфигурации: {e}")
    raise
