import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from ..app.models.base import Base
from ..app.models.booking import Booking as BookingModel, BookingStatus
from ..app.models.settings import StudioSettings
from ..app.services.booking import BookingService
from ..app.schemas.booking import BookingCreate
import json

# Тестовая база данных настраивается в conftest.py
# Фикстура для сервиса бронирования
@pytest.fixture
def booking_service(db_session):
    return BookingService(db_session)

# Фикстура studio_settings теперь в conftest.py

# --- Тесты валидации ---

def test_create_booking_in_past_fails(booking_service, studio_settings):
    """Тест: нельзя забронировать время в прошлом."""
    past_time = datetime.now(timezone.utc) - timedelta(days=1)
    booking_data = BookingCreate(
        start_time=past_time,
        end_time=past_time + timedelta(hours=1),
        date=past_time,
        client_name="Test", client_phone="123", total_price=1000
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(booking_data)
    assert excinfo.value.status_code == 400
    assert "прошедшее время" in excinfo.value.detail

def test_create_booking_overlapping_fails(booking_service, studio_settings):
    """Тест: нельзя забронировать время, которое уже занято."""
    now = datetime.now(timezone.utc)
    start_time = datetime(now.year + 1, 5, 17, 12, 0, tzinfo=timezone.utc) # Пятница

    # Создаем существующее бронирование
    existing_booking = BookingModel(
        start_time=start_time,
        end_time=start_time + timedelta(hours=2),
        date=start_time,
        status=BookingStatus.CONFIRMED,
        client_name="Old Client", client_phone="000", total_price=2000
    )
    booking_service.db.add(existing_booking)
    booking_service.db.commit()

    # Пытаемся создать пересекающееся бронирование
    overlapping_data = BookingCreate(
        start_time=start_time + timedelta(hours=1),
        end_time=start_time + timedelta(hours=3),
        date=start_time,
        client_name="New Client", client_phone="111", total_price=2000
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(overlapping_data)
    assert excinfo.value.status_code == 409
    assert "уже занято" in excinfo.value.detail

def test_create_booking_on_weekend_fails(booking_service, studio_settings):
    """Тест: нельзя забронировать в нерабочий день (воскресенье)."""
    now = datetime.now(timezone.utc)
    # Находим ближайшее воскресенье
    sunday = now + timedelta(days=(6 - now.weekday()))
    start_time = datetime(sunday.year, sunday.month, sunday.day, 14, 0, tzinfo=timezone.utc)

    booking_data = BookingCreate(
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        date=start_time,
        client_name="Test", client_phone="123", total_price=1000
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(booking_data)
    assert excinfo.value.status_code == 400
    assert "не работает в этот день недели" in excinfo.value.detail

def test_create_booking_on_holiday_fails(booking_service, studio_settings):
    """Тест: нельзя забронировать в праздничный день."""
    start_time = datetime(2025, 1, 1, 14, 0, tzinfo=timezone.utc) # 1 января
    booking_data = BookingCreate(
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        date=start_time,
        client_name="Test", client_phone="123", total_price=1000
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(booking_data)
    assert excinfo.value.status_code == 400
    assert "не работает в праздничные дни" in excinfo.value.detail


def test_create_booking_outside_working_hours_fails(booking_service, studio_settings):
    """Тест: нельзя забронировать время раньше открытия или позже закрытия."""
    now = datetime.now(timezone.utc)
    start_time = datetime(now.year + 1, 5, 17, 9, 0, tzinfo=timezone.utc) # 9 утра, до открытия

    booking_data = BookingCreate(
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        date=start_time,
        client_name="Test", client_phone="123", total_price=1000
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(booking_data)
    assert excinfo.value.status_code == 400
    assert "за рамки рабочего времени" in excinfo.value.detail

def test_create_valid_booking_succeeds(booking_service, studio_settings):
    """Тест: успешное создание валидного бронирования."""
    now = datetime.now(timezone.utc)
    start_time = datetime(now.year + 1, 5, 17, 15, 0, tzinfo=timezone.utc) # Пятница, 15:00

    booking_data = BookingCreate(
        start_time=start_time,
        end_time=start_time + timedelta(hours=2),
        date=start_time,
        client_name="Valid Client", client_phone="777", total_price=2000
    )

    # Этот вызов не должен вызывать исключений
    new_booking = booking_service.create_booking(booking_data)
    assert new_booking is not None
    assert new_booking.client_name == "Valid Client"
    assert new_booking.status == BookingStatus.PENDING # По умолчанию
