from fastapi import APIRouter
from .routes import (
    employees_enhanced,
    bookings_enhanced,
    kanban,
    websocket
)

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(employees_enhanced.router)
api_router.include_router(bookings_enhanced.router)
api_router.include_router(kanban.router)
api_router.include_router(websocket.router)