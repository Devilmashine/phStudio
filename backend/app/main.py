import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


# Настройка логирования
def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5),
        ],
    )


# Инициализация логирования
setup_logging()
logger = logging.getLogger(__name__)

# Импорты вынесены в начало файла для лучшей читаемости
from .core.config import get_settings
from .core.rate_limiter import setup_rate_limiter, default_rate_limit
from .core.cache import setup_cache
from .services.telegram_bot import TelegramBotService
from .api.routes.calendar_events import router as calendar_events_router
from .api.routes.settings import router as settings_router
from .api.routes.gallery import router as gallery_router
from .api.routes.news import router as news_router
from .api.routes.auth import router as auth_router
from .api.routes.booking import router as booking_router


def create_app() -> FastAPI:
    # Создаем экземпляр FastAPI
    app = FastAPI(
        title="phStudio API",
        description="API для фотостудии",
        version="1.0.0",
        redirect_slashes=False,
        dependencies=[
            Depends(default_rate_limit)
        ],  # Применяем rate-limit ко всем эндпоинтам
    )

    # Настраиваем CORS из настроек
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        """Инициализация сервисов при запуске"""
        try:
            # Инициализация rate limiter
            await setup_rate_limiter()
            # Инициализация кэширования
            await setup_cache()
            logger.info("Rate limiter and cache services initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing services: {str(e)}")

    # Регистрируем роутеры
    app.include_router(calendar_events_router)
    app.include_router(settings_router)
    app.include_router(gallery_router)
    app.include_router(news_router)
    app.include_router(auth_router)
    app.include_router(booking_router)

    # Инициализация Telegram бота
    try:
        TelegramBotService()
        logger.info("Telegram Bot Service successfully initialized")
    except Exception as e:
        logger.error(f"Error initializing Telegram Bot Service: {str(e)}")

    return app


app = create_app()
