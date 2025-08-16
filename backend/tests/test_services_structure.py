import pytest

def test_booking_service():
    """Тест сервиса бронирования."""
    from ..app.services.booking import BookingService
    
    # Проверяем, что сервис существует
    assert BookingService is not None

def test_calendar_event_service():
    """Тест сервиса календарных событий."""
    from ..app.services.calendar_event import CalendarEventService
    
    # Проверяем, что сервис существует
    assert CalendarEventService is not None

def test_client_service():
    """Тест сервиса клиентов."""
    from ..app.services.client import ClientService
    
    # Проверяем, что сервис существует
    assert ClientService is not None

def test_gallery_service():
    """Тест сервиса галереи."""
    from ..app.services.gallery import GalleryService
    
    # Проверяем, что сервис существует
    assert GalleryService is not None

def test_news_service():
    """Тест сервиса новостей."""
    from ..app.services.news import get_news, get_news_by_id, create_news, update_news, delete_news
    
    # Проверяем, что функции сервиса существуют
    assert callable(get_news)
    assert callable(get_news_by_id)
    assert callable(create_news)
    assert callable(update_news)
    assert callable(delete_news)

def test_settings_service():
    """Тест сервиса настроек."""
    from ..app.services.settings import StudioSettingsService
    
    # Проверяем, что сервис существует
    assert StudioSettingsService is not None

def test_user_service():
    """Тест сервиса пользователей."""
    from ..app.services.user import UserService
    
    # Проверяем, что сервис существует
    assert UserService is not None

def test_telegram_bot_service():
    """Тест сервиса Telegram бота."""
    from ..app.services.telegram_bot import TelegramBotService
    
    # Проверяем, что сервис существует
    assert TelegramBotService is not None
