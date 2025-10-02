from fastapi import APIRouter
from .routes import (
    employees_enhanced,
    bookings_enhanced,
    kanban,
    websocket,
    employee_crm,
    gallery,
    news,
    settings,
    calendar_events,
    auth,
)

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(employees_enhanced.router)
api_router.include_router(bookings_enhanced.router)
api_router.include_router(kanban.router)
api_router.include_router(websocket.router)
api_router.include_router(employee_crm.router)
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(gallery.router, prefix="/gallery", tags=["gallery"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(calendar_events.router, prefix="/calendar-events", tags=["calendar-events"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])