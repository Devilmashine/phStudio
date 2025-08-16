import pytest

@pytest.mark.unit
@pytest.mark.models
def test_user_model_structure():
    """Тест структуры модели User."""
    from ..app.models.user import User, UserRole
    
    # Проверяем, что модель имеет необходимые поля
    assert hasattr(User, 'id')
    assert hasattr(User, 'username')
    assert hasattr(User, 'email')
    assert hasattr(User, 'hashed_password')
    assert hasattr(User, 'role')
    assert hasattr(User, 'full_name')
    assert hasattr(User, 'created_at')
    assert hasattr(User, 'last_login')
    assert hasattr(User, 'ical_token')
    
    # Проверяем enum
    assert UserRole.admin in UserRole
    assert UserRole.manager in UserRole
    assert UserRole.user in UserRole

@pytest.mark.unit
@pytest.mark.models
def test_booking_model_structure():
    """Тест структуры модели Booking."""
    from ..app.models.booking import Booking, BookingStatus
    
    # Проверяем, что модель имеет необходимые поля
    assert hasattr(Booking, 'id')
    assert hasattr(Booking, 'date')
    assert hasattr(Booking, 'start_time')
    assert hasattr(Booking, 'end_time')
    assert hasattr(Booking, 'status')
    assert hasattr(Booking, 'total_price')
    assert hasattr(Booking, 'client_name')
    assert hasattr(Booking, 'client_phone')
    assert hasattr(Booking, 'client_email')
    assert hasattr(Booking, 'phone_normalized')
    assert hasattr(Booking, 'notes')
    assert hasattr(Booking, 'created_at')
    assert hasattr(Booking, 'updated_at')
    assert hasattr(Booking, 'calendar_event_id')
    
    # Проверяем enum
    assert BookingStatus.PENDING in BookingStatus
    assert BookingStatus.CONFIRMED in BookingStatus
    assert BookingStatus.CANCELLED in BookingStatus
    assert BookingStatus.COMPLETED in BookingStatus

@pytest.mark.unit
@pytest.mark.models
def test_calendar_event_model_structure():
    """Тест структуры модели CalendarEvent."""
    from ..app.models.calendar_event import CalendarEvent
    from ..app.models.calendar_event_status import CalendarEventStatus
    
    # Проверяем, что модель имеет необходимые поля
    assert hasattr(CalendarEvent, 'id')
    assert hasattr(CalendarEvent, 'title')
    assert hasattr(CalendarEvent, 'description')
    assert hasattr(CalendarEvent, 'start_time')
    assert hasattr(CalendarEvent, 'end_time')
    assert hasattr(CalendarEvent, 'people_count')
    assert hasattr(CalendarEvent, 'status')
    assert hasattr(CalendarEvent, 'availability_cached')
    assert hasattr(CalendarEvent, 'cache_updated_at')
    assert hasattr(CalendarEvent, 'created_at')
    assert hasattr(CalendarEvent, 'updated_at')
    assert hasattr(CalendarEvent, 'bookings')
    
    # Проверяем enum
    assert CalendarEventStatus.pending in CalendarEventStatus

@pytest.mark.unit
@pytest.mark.models
def test_settings_model_structure():
    """Тест структуры модели StudioSettings."""
    from ..app.models.settings import StudioSettings
    
    # Проверяем, что модель имеет необходимые поля
    assert hasattr(StudioSettings, 'id')
    assert hasattr(StudioSettings, 'name')
    assert hasattr(StudioSettings, 'description')
    assert hasattr(StudioSettings, 'contacts')
    assert hasattr(StudioSettings, 'prices')
    assert hasattr(StudioSettings, 'work_days')
    assert hasattr(StudioSettings, 'work_start_time')
    assert hasattr(StudioSettings, 'work_end_time')
    assert hasattr(StudioSettings, 'base_price_per_hour')
    assert hasattr(StudioSettings, 'weekend_price_multiplier')
    assert hasattr(StudioSettings, 'telegram_notifications_enabled')
    assert hasattr(StudioSettings, 'email_notifications_enabled')
    assert hasattr(StudioSettings, 'holidays')
    assert hasattr(StudioSettings, 'min_booking_duration')
    assert hasattr(StudioSettings, 'max_booking_duration')
    assert hasattr(StudioSettings, 'advance_booking_days')

@pytest.mark.unit
@pytest.mark.models
def test_client_model_structure():
    """Тест структуры модели Client."""
    from ..app.models.client import Client
    
    # Проверяем, что модель имеет необходимые поля
    assert hasattr(Client, 'id')
    assert hasattr(Client, 'name')
    assert hasattr(Client, 'phone')
    assert hasattr(Client, 'email')
    assert hasattr(Client, 'created_at')
    assert hasattr(Client, 'updated_at')
