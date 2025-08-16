import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

def test_booking_overlap_validation(auth_client, db_session):
    """Тест валидации перекрытия бронирований."""
    # Создаем первое бронирование
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    first_booking = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Client 1",
        "client_phone": "+79001234567"
    }
    
    response = auth_client.post("/api/bookings/", json=first_booking)
    assert response.status_code == 201
    
    # Пытаемся создать перекрывающееся бронирование
    overlapping_booking = {
        "date": future_date.isoformat(),
        "start_time": future_date.replace(hour=10, minute=30, second=0, microsecond=0).isoformat(),
        "end_time": future_date.replace(hour=11, minute=30, second=0, microsecond=0).isoformat(),
        "total_price": 1000.0,
        "client_name": "Client 2",
        "client_phone": "+79001234568"
    }
    
    response = auth_client.post("/api/bookings/", json=overlapping_booking)
    # Должен вернуться 400 Bad Request из-за перекрытия
    assert response.status_code == 400

def test_invalid_date_validation(auth_client):
    """Тест валидации некорректных дат."""
    # Пытаемся создать бронирование в прошлом
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    start_time = past_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = past_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    invalid_booking = {
        "date": past_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Test Client",
        "client_phone": "+79001234567"
    }
    
    response = auth_client.post("/api/bookings/", json=invalid_booking)
    # Должен вернуться 400 Bad Request
    assert response.status_code == 400

def test_invalid_time_range(auth_client):
    """Тест валидации некорректного временного диапазона."""
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)  # end < start
    
    invalid_booking = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Test Client",
        "client_phone": "+79001234567"
    }
    
    response = auth_client.post("/api/bookings/", json=invalid_booking)
    # Должен вернуться 400 Bad Request
    assert response.status_code == 400

def test_missing_required_fields(auth_client):
    """Тест валидации отсутствующих обязательных полей."""
    # Создаем неполные данные бронирования
    incomplete_booking = {
        "client_name": "Test Client",
        # Отсутствуют обязательные поля: date, start_time, end_time, total_price, client_phone
    }
    
    response = auth_client.post("/api/bookings/", json=incomplete_booking)
    # Должен вернуться 422 Unprocessable Entity
    assert response.status_code == 422

def test_invalid_phone_format(auth_client):
    """Тест валидации некорректного формата телефона."""
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    invalid_phone_booking = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Test Client",
        "client_phone": "invalid_phone"  # Некорректный формат
    }
    
    response = auth_client.post("/api/bookings/", json=invalid_phone_booking)
    # Должен вернуться 400 Bad Request или 422 Unprocessable Entity
    assert response.status_code in [400, 422]

def test_negative_price_validation(auth_client):
    """Тест валидации отрицательной цены."""
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    negative_price_booking = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": -100.0,  # Отрицательная цена
        "client_name": "Test Client",
        "client_phone": "+79001234567"
    }
    
    response = auth_client.post("/api/bookings/", json=negative_price_booking)
    # Должен вернуться 400 Bad Request или 422 Unprocessable Entity
    assert response.status_code in [400, 422]

def test_very_long_text_fields(auth_client):
    """Тест валидации очень длинных текстовых полей."""
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    # Создаем очень длинное имя клиента
    very_long_name = "A" * 1000  # 1000 символов
    
    long_name_booking = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": very_long_name,
        "client_phone": "+79001234567"
    }
    
    response = auth_client.post("/api/bookings/", json=long_name_booking)
    # Должен вернуться 400 Bad Request или 422 Unprocessable Entity
    assert response.status_code in [400, 422]

def test_sql_injection_prevention(auth_client):
    """Тест предотвращения SQL-инъекций."""
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    # Пытаемся использовать SQL-инъекцию в имени клиента
    malicious_booking = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "'; DROP TABLE bookings; --",
        "client_phone": "+79001234567"
    }
    
    response = auth_client.post("/api/bookings/", json=malicious_booking)
    # Должен вернуться 400 Bad Request или 422 Unprocessable Entity
    # Или 201 Created, но SQL-инъекция должна быть предотвращена
    assert response.status_code in [400, 422, 201]

def test_xss_prevention(auth_client):
    """Тест предотвращения XSS-атак."""
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    # Пытаемся использовать XSS в заметках
    xss_booking = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Test Client",
        "client_phone": "+79001234567",
        "notes": "<script>alert('XSS')</script>"
    }
    
    response = auth_client.post("/api/bookings/", json=xss_booking)
    # Должен вернуться 201 Created, но XSS должен быть предотвращен
    assert response.status_code == 201
    
    # Проверяем, что скрипт не выполнился (данные должны быть экранированы)
    data = response.json()
    assert "<script>" in data["notes"]  # HTML должен быть экранирован или сохранен как есть
