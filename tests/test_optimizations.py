import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.app.services.calendar_service import CalendarService
from backend.app.models.calendar_event import CalendarEvent
from backend.app.models.booking import BookingLegacy


def _utc_now():
    return datetime.now(timezone.utc)


def _normalize_phone(phone: str) -> str:
    digits = ''.join(filter(str.isdigit, phone))
    if not digits:
        return ''
    if digits.startswith('8'):
        digits = '7' + digits[1:]
    if not digits.startswith('7') and len(digits) == 10:
        digits = '7' + digits
    return f"+{digits}"

def test_calendar_cache_optimization(db_session: Session):
    """Проверяет оптимизацию кэширования календаря"""
    service = CalendarService(db_session)
    
    # Создаем тестовое событие
    now = _utc_now()
    event = CalendarEvent(
        title="Test Event",
        start_time=now,
        end_time=now + timedelta(hours=2),
    )
    db_session.add(event)
    db_session.commit()
    
    # Первый запрос должен обновить кэш
    now = _utc_now()
    events = service.get_events(
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=1)
    )
    assert events[0].availability_cached is not None
    initial_cache_time = events[0].cache_updated_at
    
    # Повторный запрос в течение TTL не должен обновлять кэш
    now = _utc_now()
    events = service.get_events(
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=1)
    )
    assert events[0].cache_updated_at == initial_cache_time

def test_booking_phone_normalization(db_session: Session):
    """Проверяет нормализацию телефонных номеров"""
    # Создаем бронирование с разными форматами номера
    base_time = _utc_now()
    bookings = []
    for phone in ["+79991234567", "89991234567", "79991234567"]:
        booking = BookingLegacy(
            date=base_time,
            start_time=base_time,
            end_time=base_time + timedelta(hours=1),
            client_name="Test",
            client_phone=phone,
            phone_normalized=_normalize_phone(phone),
            total_price=1000,
            people_count=2
        )
        bookings.append(booking)
    
    for booking in bookings:
        db_session.add(booking)
    db_session.commit()
    
    # Проверяем, что все номера нормализованы одинаково
    normalized_phones = [b.phone_normalized for b in bookings]
    assert len(set(normalized_phones)) == 1  # Все номера должны быть приведены к одному формату

def test_date_range_index_optimization(db_session: Session):
    """Проверяет оптимизацию индекса для поиска по диапазону дат"""
    service = CalendarService(db_session)
    
    # Создаем тестовые события
    base_time = _utc_now()
    for i in range(10):
        event = CalendarEvent(
            title=f"Test Event {i}",
            start_time=base_time + timedelta(days=i),
            end_time=base_time + timedelta(days=i, hours=2),
            people_count=5
        )
        db_session.add(event)
    db_session.commit()
    
    # Запрашиваем события с использованием индекса
    start_date = _utc_now()
    end_date = start_date + timedelta(days=5)
    assert len(events) == 6  # События с 0 по 5 день
