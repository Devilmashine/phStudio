import pytest

def test_booking_schemas():
    """Тест схем бронирования."""
    from app.schemas.booking import BookingCreate, Booking, BookingStatusUpdate
    
    # Проверяем, что схемы существуют
    assert BookingCreate is not None
    assert Booking is not None
    assert BookingStatusUpdate is not None

def test_calendar_event_schemas():
    """Тест схем календарных событий."""
    from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse
    
    # Проверяем, что схемы существуют
    assert CalendarEventCreate is not None
    assert CalendarEventUpdate is not None
    assert CalendarEventResponse is not None

def test_client_schemas():
    """Тест схем клиентов."""
    from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
    
    # Проверяем, что схемы существуют
    assert ClientCreate is not None
    assert ClientUpdate is not None
    assert ClientResponse is not None

def test_gallery_schemas():
    """Тест схем галереи."""
    from app.schemas.gallery import GalleryImageCreate, GalleryImage
    
    # Проверяем, что схемы существуют
    assert GalleryImageCreate is not None
    assert GalleryImage is not None

def test_news_schemas():
    """Тест схем новостей."""
    from app.schemas.news import NewsCreate, NewsUpdate, News
    
    # Проверяем, что схемы существуют
    assert NewsCreate is not None
    assert NewsUpdate is not None
    assert News is not None

def test_settings_schemas():
    """Тест схем настроек."""
    from app.schemas.settings import StudioSettingsCreate, StudioSettingsUpdate, StudioSettings
    
    # Проверяем, что схемы существуют
    assert StudioSettingsCreate is not None
    assert StudioSettingsUpdate is not None
    assert StudioSettings is not None

def test_user_schemas():
    """Тест схем пользователей."""
    from app.schemas.user import UserCreate, UserUpdate, UserResponse
    
    # Проверяем, что схемы существуют
    assert UserCreate is not None
    assert UserUpdate is not None
    assert UserResponse is not None
