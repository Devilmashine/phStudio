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

# Создание приложения FastAPI с отключенными автоматическими редиректами
app = FastAPI(
    title="phStudio API",
    description="API для фотостудии",
    version="1.0.0",
    # Отключаем редиректы глобально для всего приложения
    redirect_slashes=False
)


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.rate_limiter import setup_rate_limiter, default_rate_limit
from app.core.cache import setup_cache, cache_calendar_state, cache_settings, cache_gallery
from app.services.telegram_bot import TelegramBotService
from app.api.routes.calendar_events import router as calendar_events_router
from app.api.routes.settings import router as settings_router
from app.api.routes.gallery import router as gallery_router
from app.api.routes.news import router as news_router
from app.api.routes.auth import router as auth_router
from app.api.routes.booking import router as booking_router
from app.api.routes.employees import router as employees_router
from app.api.routes.clients import router as clients_router

@app.on_event("startup")
async def startup_event():
    """Инициализация сервисов при запуске"""
    # Не инициализируем Redis в тестовом окружении
    if os.environ.get("ENV") == "testing":
        return
    try:
        await setup_rate_limiter()
        await setup_cache()
        logger.info("Rate limiter and cache services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")


# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://laughing-waffle-g7xxww4jqwwcg7q-5173.app.github.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# for router in [
#     calendar_events_router,
#     settings_router,
#     gallery_router,
#     news_router,
#     booking_router,
#     employees_router
# ]:
#     for route in getattr(router, "routes", []):
#         if hasattr(route, "dependencies"):
#             route.dependencies.append(Depends(default_rate_limit))


def include_routers(app: FastAPI):
    app.include_router(calendar_events_router, prefix="/api", tags=["calendar"])
    app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
    app.include_router(gallery_router, prefix="/api/gallery", tags=["gallery"])
    app.include_router(news_router, prefix="/api/news", tags=["news"])
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(booking_router, prefix="/api/bookings", tags=["bookings"])
    app.include_router(employees_router, prefix="/api/employees", tags=["employees"])
    app.include_router(clients_router, prefix="/api/clients", tags=["clients"])

include_routers(app)


# Инициализация Telegram бота
try:
    telegram_service = TelegramBotService()
    logger.info("Telegram Bot Service successfully initialized")
except Exception as e:
    logger.error(f"Error initializing Telegram Bot Service: {str(e)}")
    telegram_service = None
