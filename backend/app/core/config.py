from pydantic_settings import BaseSettings
from typing import List
from pydantic import computed_field

class Settings(BaseSettings):
    # --- Основные настройки ---
    ENV: str = "development"
    DATABASE_URL: str

    # --- Безопасность ---
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200
    ALGORITHM: str = "HS256"

    # --- CORS ---
    CORS_ORIGINS_STR: str = ""

    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if not self.CORS_ORIGINS_STR:
            return []
        return [i.strip() for i in self.CORS_ORIGINS_STR.split(",") if i.strip()]

    # --- Интеграции ---
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    class Config:
        # Pydantic-settings会自动从.env файле читать переменные
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()
