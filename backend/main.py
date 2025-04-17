from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import booking_router, calendar_router, telegram_router, stats_router
from config import settings

# Create FastAPI instance
app = FastAPI(title="Photo Studio API")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(booking_router, prefix="/api/bookings", tags=["bookings"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["calendar"])
app.include_router(telegram_router, prefix="/api/telegram", tags=["telegram"])
app.include_router(stats_router, prefix="/api/stats", tags=["statistics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
