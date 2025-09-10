import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import time_machine

from ..app.models.booking import BookingLegacy as BookingModel, BookingStatus
from ..app.services.booking import BookingService
from ..app.schemas.booking import BookingCreate

@pytest.fixture
def booking_service(db_session):
    return BookingService(db_session)

@pytest.mark.parametrize("travel_to", [datetime(2025, 8, 11, 10, 0, tzinfo=timezone.utc)])
def test_create_booking_in_past_fails(booking_service, studio_settings, travel_to, time_machine):
    """Тест: нельзя забронировать время в прошлом."""
    time_machine.move_to(travel_to)
    past_time = datetime.now(timezone.utc) - timedelta(days=1)
    booking_data = BookingCreate(
        start_time=past_time,
        end_time=past_time + timedelta(hours=1),
        date=past_time.date(),
        client_name="Test", client_phone="123", total_price=1000,
        people_count=1
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(booking_data)
    assert excinfo.value.status_code == 400
    assert "прошедшее время" in excinfo.value.detail

@pytest.mark.parametrize("travel_to", [datetime(2025, 8, 11, 10, 0, tzinfo=timezone.utc)])
def test_create_booking_overlapping_fails(booking_service, studio_settings, travel_to, time_machine):
    """Тест: нельзя забронировать время, которое уже занято."""
    time_machine.move_to(travel_to)
    start_time = datetime.now(timezone.utc) + timedelta(days=1, hours=2) # Tuesday 12:00

    existing_booking = BookingModel(
        start_time=start_time,
        end_time=start_time + timedelta(hours=2),
        date=start_time.date(),
        status=BookingStatus.CONFIRMED,
        client_name="Old Client", client_phone="000", total_price=2000,
        people_count=1
    )
    booking_service.db.add(existing_booking)
    booking_service.db.commit()

    overlapping_data = BookingCreate(
        start_time=start_time + timedelta(hours=1),
        end_time=start_time + timedelta(hours=3),
        date=start_time.date(),
        client_name="New Client", client_phone="111", total_price=2000,
        people_count=1
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(overlapping_data)
    assert excinfo.value.status_code == 409
    assert "уже занято" in excinfo.value.detail

@pytest.mark.parametrize("travel_to", [datetime(2025, 8, 11, 10, 0, tzinfo=timezone.utc)])
def test_create_booking_on_weekend_fails(booking_service, studio_settings, travel_to, time_machine):
    """Тест: нельзя забронировать в нерабочий день (воскресенье)."""
    time_machine.move_to(travel_to)
    now = datetime.now(timezone.utc)
    sunday = now + timedelta(days=(6 - now.weekday()))
    start_time = datetime(sunday.year, sunday.month, sunday.day, 14, 0, tzinfo=timezone.utc)

    booking_data = BookingCreate(
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        date=start_time.date(),
        client_name="Test", client_phone="123", total_price=1000,
        people_count=1
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(booking_data)
    assert excinfo.value.status_code == 400
    assert "не работает в этот день недели" in excinfo.value.detail

@pytest.mark.parametrize("travel_to", [datetime(2025, 8, 11, 10, 0, tzinfo=timezone.utc)])
def test_create_booking_on_holiday_fails(booking_service, studio_settings, travel_to, time_machine):
    """Тест: нельзя забронировать в праздничный день."""
    time_machine.move_to(travel_to)
    future_holiday = datetime(2026, 1, 1, 14, 0, tzinfo=timezone.utc)
    studio_settings.holidays = '["2026-01-01"]'
    booking_service.db.commit()

    booking_data = BookingCreate(
        start_time=future_holiday,
        end_time=future_holiday + timedelta(hours=1),
        date=future_holiday.date(),
        client_name="Test", client_phone="123", total_price=1000,
        people_count=1
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(booking_data)
    assert excinfo.value.status_code == 400
    assert "не работает в праздничные дни" in excinfo.value.detail

@pytest.mark.parametrize("travel_to", [datetime(2025, 8, 11, 10, 0, tzinfo=timezone.utc)])
def test_create_booking_outside_working_hours_fails(booking_service, studio_settings, travel_to, time_machine):
    """Тест: нельзя забронировать время раньше открытия или позже закрытия."""
    time_machine.move_to(travel_to)
    start_time = datetime.now(timezone.utc).replace(hour=9, minute=0) + timedelta(days=1)

    booking_data = BookingCreate(
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        date=start_time.date(),
        client_name="Test", client_phone="123", total_price=1000,
        people_count=1
    )
    with pytest.raises(HTTPException) as excinfo:
        booking_service.create_booking(booking_data)
    assert excinfo.value.status_code == 400
    assert "за рамки рабочего времени" in excinfo.value.detail

@pytest.mark.parametrize("travel_to", [datetime(2025, 8, 11, 10, 0, tzinfo=timezone.utc)])
def test_create_valid_booking_succeeds(booking_service, studio_settings, travel_to, time_machine):
    """Тест: успешное создание валидного бронирования."""
    time_machine.move_to(travel_to)
    start_time = datetime.now(timezone.utc).replace(hour=15, minute=0) + timedelta(days=1)

    booking_data = BookingCreate(
        start_time=start_time,
        end_time=start_time + timedelta(hours=2),
        date=start_time.date(),
        client_name="Valid Client", client_phone="777", total_price=2000,
        people_count=1
    )

    new_booking = booking_service.create_booking(booking_data)
    assert new_booking is not None
    assert new_booking.client_name == "Valid Client"
    assert new_booking.status == BookingStatus.PENDING
