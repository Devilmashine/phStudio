import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

def test_create_booking_success(auth_client, db_session):
    """Тест успешного создания бронирования через API."""
    from ..app.schemas.booking import BookingCreate
    
    # Создаем данные для бронирования
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    booking_data = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Test Client",
        "client_phone": "+79001234567",
        "client_email": "test@example.com",
        "notes": "Test booking"
    }
    
    # Отправляем запрос на создание бронирования
    response = auth_client.post("/api/bookings/", json=booking_data)
    
    # Проверяем успешный ответ
    assert response.status_code == 201
    data = response.json()
    assert data["client_name"] == "Test Client"
    assert data["client_phone"] == "+79001234567"
    assert data["status"] == "pending"

def test_get_bookings_list(auth_client, db_session):
    """Тест получения списка бронирований через API."""
    # Отправляем запрос на получение списка бронирований
    response = auth_client.get("/api/bookings/")
    
    # Проверяем успешный ответ
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_booking_by_id(auth_client, db_session):
    """Тест получения бронирования по ID через API."""
    # Сначала создаем бронирование
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    booking_data = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Test Client 2",
        "client_phone": "+79001234568",
        "client_email": "test2@example.com"
    }
    
    create_response = auth_client.post("/api/bookings/", json=booking_data)
    assert create_response.status_code == 201
    created_booking = create_response.json()
    booking_id = created_booking["id"]
    
    # Теперь получаем бронирование по ID
    response = auth_client.get(f"/api/bookings/{booking_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == booking_id
    assert data["client_name"] == "Test Client 2"

def test_update_booking_status(auth_client, db_session):
    """Тест обновления статуса бронирования через API."""
    # Сначала создаем бронирование
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    booking_data = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Test Client 3",
        "client_phone": "+79001234569",
        "client_email": "test3@example.com"
    }
    
    create_response = auth_client.post("/api/bookings/", json=booking_data)
    assert create_response.status_code == 201
    created_booking = create_response.json()
    booking_id = created_booking["id"]
    
    # Обновляем статус на "confirmed"
    status_update = {"status": "confirmed"}
    response = auth_client.patch(f"/api/bookings/{booking_id}/status", json=status_update)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"

def test_delete_booking(auth_client, db_session):
    """Тест удаления бронирования через API."""
    # Сначала создаем бронирование
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    booking_data = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Test Client 4",
        "client_phone": "+79001234570",
        "client_email": "test4@example.com"
    }
    
    create_response = auth_client.post("/api/bookings/", json=booking_data)
    assert create_response.status_code == 201
    created_booking = create_response.json()
    booking_id = created_booking["id"]
    
    # Удаляем бронирование
    response = auth_client.delete(f"/api/bookings/{booking_id}")
    assert response.status_code == 204
    
    # Проверяем, что бронирование действительно удалено
    get_response = auth_client.get(f"/api/bookings/{booking_id}")
    assert get_response.status_code == 404
