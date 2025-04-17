from .booking import router as booking_router
from .calendar import router as calendar_router
from .telegram import router as telegram_router
from .stats_router import router as stats_router

__all__ = ["booking_router", "calendar_router", "telegram_router", "stats_router"]
