from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1.api import api_router
from app.api import booking_router, calendar_router, telegram_router, stats_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Подключение роутеров
app.include_router(booking_router, prefix="/api/v1")
app.include_router(calendar_router, prefix="/api/v1")
app.include_router(telegram_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy"} 