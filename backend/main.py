from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import booking, calendar, telegram
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
app.include_router(booking.router, prefix="/api/bookings", tags=["bookings"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["telegram"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
