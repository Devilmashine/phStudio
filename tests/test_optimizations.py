import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.services.calendar_service import CalendarService
from backend.app.models.calendar_event import CalendarEvent
from backend.app.models.booking import Booking, BookingStatus

def test_calendar_cache_optimization(db_session: Session):
    """Проверяет оптимизацию кэширования календаря"""
    service = CalendarService(db_session)
    
    # Создаем тестовое событие
    event = CalendarEvent(
        title="Test Event",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=2),
        people_count=5
    )
    db_session.add(event)
    db_session.commit()
    
    # Первый запрос должен обновить кэш
    events = service.get_events(
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now() + timedelta(days=1)
    )
    assert events[0].availability_cached is not None
    initial_cache_time = events[0].cache_updated_at
    
    # Повторный запрос в течение TTL не должен обновлять кэш
    events = service.get_events(
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now() + timedelta(days=1)
    )
    assert events[0].cache_updated_at == initial_cache_time

def test_booking_phone_normalization(db_session: Session):
    """Проверяет нормализацию телефонных номеров"""
    # Создаем бронирование с разными форматами номера
    bookings = [
        Booking(
            date=datetime.now(),
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            client_name="Test",
            client_phone=phone,
            total_price=1000,
            people_count=2
        )
        for phone in ["+79991234567", "89991234567", "79991234567"]
    ]
    
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
    for i in range(10):
        event = CalendarEvent(
            title=f"Test Event {i}",
            start_time=datetime.now() + timedelta(days=i),
            end_time=datetime.now() + timedelta(days=i, hours=2),
            people_count=5
        )
        db_session.add(event)
    db_session.commit()
    
    # Запрашиваем события с использованием индекса
    start_date = datetime.now()
    end_date = datetime.now() + timedelta(days=5)
    
    events = service.get_events(start_date=start_date, end_date=end_date)
    assert len(events) == 6  # События с 0 по 5 день
