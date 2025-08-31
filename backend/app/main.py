import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.security import SecurityHeadersMiddleware, RateLimitMiddleware, InputValidationMiddleware
from app.core.config import get_settings


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
    description="Secure API для фотостудии",
    version="1.0.0",
    # Отключаем редиректы глобально для всего приложения
    redirect_slashes=False,
    # Security configurations
    docs_url="/docs" if not get_settings().IS_PRODUCTION else None,
    redoc_url="/redoc" if not get_settings().IS_PRODUCTION else None,
)


# Security middleware configuration
settings = get_settings()

# Add input validation middleware (first in chain for security)
app.add_middleware(InputValidationMiddleware)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting middleware (cost-effective in-memory solution)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)

# Add trusted host middleware for production
if settings.IS_PRODUCTION:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["yourdomain.com", "*.yourdomain.com", "localhost"]
    )

# Secure CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Secure: specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "X-CSRF-Token"
    ],
    expose_headers=["X-Total-Count", "X-Request-ID", "X-Process-Time"],
    max_age=86400,  # Cache preflight for 24 hours
)

from app.core.rate_limiter import setup_rate_limiter, default_rate_limit
from app.core.cache import setup_cache, cache_calendar_state, cache_settings, cache_gallery
from app.api.routes.calendar_events import router as calendar_events_router
from app.api.routes.calendar import router as calendar_router
from app.api.routes.settings import router as settings_router
from app.api.routes.gallery import router as gallery_router
from app.api.routes.news import router as news_router
from app.api.routes.auth import router as auth_router
from app.api.routes.booking import router as booking_router
from app.api.routes.employees import router as employees_router
from app.api.routes.telegram import router as telegram_router
from app.api.routes.consent import router as consent_router
from app.api.routes.legal_documents import router as legal_documents_router
from app.api.main_router import api_router

# Debug router for Telegram configuration
from fastapi import APIRouter
from app.core.config import get_settings
import functools

debug_router = APIRouter(prefix="/debug", tags=["debug"])

@debug_router.get("/telegram-config")
async def debug_telegram_config():
    """Debug endpoint to check Telegram configuration"""
    settings = get_settings()
    
    return {
        "telegram_bot_token": settings.TELEGRAM_BOT_TOKEN,
        "telegram_chat_id": settings.TELEGRAM_CHAT_ID,
        "token_length": len(settings.TELEGRAM_BOT_TOKEN),
        "chat_id_length": len(settings.TELEGRAM_CHAT_ID),
        "is_valid": settings.validate_telegram_config()
    }

@debug_router.get("/telegram-config-fresh")
async def debug_telegram_config_fresh():
    """Debug endpoint to check Telegram configuration with fresh settings"""
    # Clear the cache
    get_settings.cache_clear()
    
    # Get fresh settings
    settings = get_settings()
    
    return {
        "telegram_bot_token": settings.TELEGRAM_BOT_TOKEN,
        "telegram_chat_id": settings.TELEGRAM_CHAT_ID,
        "token_length": len(settings.TELEGRAM_BOT_TOKEN),
        "chat_id_length": len(settings.TELEGRAM_CHAT_ID),
        "is_valid": settings.validate_telegram_config()
    }

@debug_router.get("/cwd")
async def debug_cwd():
    """Debug endpoint to check current working directory"""
    import os
    return {
        "cwd": os.getcwd(),
        "env_file_exists": os.path.exists(".env"),
        "backend_env_file_exists": os.path.exists("backend/.env"),
        "root_env_file_exists": os.path.exists("../.env"),
        "env_vars": {
            "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
            "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID")
        }
    }

@app.on_event("startup")
async def startup_event():
    """Инициализация сервисов при запуске"""
    # Не инициализируем Redis в тестовом окружении
    from app.core.config import get_settings
    if hasattr(get_settings, "ENV") and get_settings().ENV == "testing":
        return
    
    # Initialize new Telegram service
    try:
        from app.services.telegram.service import telegram_service
        await telegram_service.initialize()
        logger.info("New Telegram service initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing new Telegram service: {str(e)}")
    
    # try:
    #     await setup_rate_limiter()
    #     await setup_cache()
    #     logger.info("Rate limiter and cache services initialized successfully")
    # except Exception as e:
    #     logger.error(f"Error initializing services: {str(e)}")


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


app.include_router(calendar_events_router, prefix="/api/calendar-events", tags=["calendar"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
app.include_router(gallery_router, prefix="/api/gallery", tags=["gallery"])
app.include_router(news_router, prefix="/api/news", tags=["news"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(booking_router, prefix="/api/bookings", tags=["bookings"])
app.include_router(employees_router, prefix="/api/employees", tags=["employees"])
app.include_router(telegram_router, prefix="/api/telegram", tags=["telegram"])
app.include_router(consent_router, prefix="/api/consent", tags=["consent"])
app.include_router(legal_documents_router, prefix="/api/legal", tags=["legal-documents"])

# Include debug router
app.include_router(debug_router)

# Include enhanced API routes
app.include_router(api_router, prefix="/api/v2", tags=["enhanced-api"])


@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown of services"""
    try:
        from app.services.telegram.service import telegram_service
        await telegram_service.shutdown()
        logger.info("Telegram service shutdown completed")
    except Exception as e:
        logger.error(f"Error during Telegram service shutdown: {str(e)}")


# Legacy Telegram service initialization (to be removed after migration)
try:
    from app.services.telegram_bot import TelegramBotService
    legacy_telegram_service = TelegramBotService()
    logger.warning("Legacy Telegram Bot Service initialized - will be deprecated")
except Exception as e:
    logger.error(f"Error initializing legacy Telegram Bot Service: {str(e)}")
    legacy_telegram_service = None
