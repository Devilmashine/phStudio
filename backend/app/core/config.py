from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    GOOGLE_CALENDAR_ID: str
    GOOGLE_CALENDAR_API_KEY: str
    GOOGLE_CLIENT_EMAIL: str
    GOOGLE_PRIVATE_KEY: str
    SERVICE_ACCOUNT_FILE: str = "backend/app/config/service_account.json"

    @field_validator("*", mode="before")
    @classmethod
    def check_not_empty(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} не может быть пустым")
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"
    }

try:
    settings = Settings()
except Exception as e:
    print(f"Ошибка загрузки конфигурации: {e}")
    raise
