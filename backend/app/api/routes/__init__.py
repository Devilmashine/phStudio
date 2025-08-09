from .calendar_events import router as calendar_events_router
from .settings import router as settings_router
from .gallery import router as gallery_router
from .news import router as news_router
from .auth import router as auth_router
from .booking import router as booking_router

__all__ = [
    'calendar_events_router',
    'settings_router',
    'gallery_router',
    'news_router',
    'auth_router',
    'booking_router'
]
