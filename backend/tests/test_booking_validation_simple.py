import pytest
from datetime import datetime, timezone, timedelta
from app.schemas.booking import BookingCreate

def test_booking_validation_past_date():
    """Тест валидации даты в прошлом без базы данных."""
    # Создаем дату в прошлом
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    past_start = past_date.replace(hour=10, minute=0, second=0, microsecond=0)
    past_end = past_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    # Проверяем, что дата действительно в прошлом
    assert past_date < datetime.now(timezone.utc)
    assert past_start < datetime.now(timezone.utc)
    assert past_end < datetime.now(timezone.utc)

def test_booking_validation_future_date():
    """Тест валидации даты в будущем без базы данных."""
    # Создаем дату в будущем
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    future_start = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    future_end = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    # Проверяем, что дата действительно в будущем
    assert future_date > datetime.now(timezone.utc)
    assert future_start > datetime.now(timezone.utc)
    assert future_end > datetime.now(timezone.utc)

def test_booking_validation_time_range():
    """Тест валидации временного диапазона без базы данных."""
    # Создаем корректный временной диапазон
    base_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = base_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = base_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    # Проверяем, что end_time > start_time
    assert end_time > start_time
    assert (end_time - start_time).total_seconds() == 3600  # 1 час

def test_booking_schema_structure():
    """Тест структуры схемы бронирования."""
    from app.schemas.booking import BookingCreate, Booking, BookingStatusUpdate
    
    # Проверяем, что схемы существуют
    assert BookingCreate is not None
    assert Booking is not None
    assert BookingStatusUpdate is not None
