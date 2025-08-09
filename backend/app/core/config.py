from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    model_config = {"env_file": str(env_path)}
    ENV: str = "development"
    CORS_ORIGINS: List[str] = []
    DATABASE_URL: str = "sqlite:///" + str(Path(__file__).parent.parent / "app.db")
    SECRET_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    # Удалены настройки Google Calendar - используем собственную реализацию календаря
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200
    ALGORITHM: str = "HS256"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v



    @field_validator("*", mode="before")
    @classmethod
    def check_not_empty(cls, v, info):
        if v is None or v == "":
            raise ValueError(f"{info.field_name} не может быть пустым")
        return v

    model_config = {
        "env_file": None,  # будет выбран ниже
        "case_sensitive": True,
        "extra": "allow"
    }

# Автоматический выбор .env файла
_env = os.getenv("ENV", "development")
_env_file = f".env.{_env}"
if not Path(_env_file).is_file():
    _env_file = ".env"
Settings.model_config["env_file"] = _env_file

try:
    settings = Settings()
except Exception as e:
    print(f"Ошибка загрузки конфигурации: {e}")
    raise
