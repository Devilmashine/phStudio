from pydantic import BaseSettings, validator
from typing import List
import os

class Settings(BaseSettings):
    CORS_ORIGINS: List[str]
    DATABASE_URL: str
    SECRET_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    GOOGLE_CALENDAR_ID: str
    GOOGLE_CALENDAR_API_KEY: str
    
    @validator("*")
    def check_not_empty(cls, v, field):
        if not v:
            raise ValueError(f"{field.name} не может быть пустым")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

try:
    settings = Settings()
except Exception as e:
    print(f"Ошибка загрузки конфигурации: {e}")
    raise
