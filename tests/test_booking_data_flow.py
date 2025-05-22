import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# Тестовые данные для бронирования
booking_payload = {
    "date": "2025-05-22",
    "times": ["10:00", "11:00"],
    "name": "Тест Клиент",
    "phone": "79999999999",
    "total_price": 2500,  # исправлено
    "service": "Студийная фотосессия"
}

calendar_event_payload = {
    "title": "Тестовое событие",
    "description": "Тестовое описание",
    "start_time": "2025-05-22T10:00:00",
    "duration_hours": 1,
    "phone": "79999999999",
    "total_price": 2500
}

def test_create_booking_full_flow():
    """Проверка полного цикла создания бронирования и передачи всех данных"""
    response = client.post("/api/bookings", json=booking_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["details"]["name"] == booking_payload["name"]
    assert data["details"]["phone"] == booking_payload["phone"]
    assert data["details"]["total_price"] == booking_payload["total_price"]
    assert data["telegram_notification"] is True or data["telegram_notification"] is False


def test_create_calendar_event_full_flow():
    """Проверка создания события календаря и передачи всех обязательных параметров"""
    response = client.post("/api/calendar/events", json=calendar_event_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data
    assert "telegram_notification" in data


def test_booking_missing_fields():
    """Проверка ошибок при отсутствии обязательных полей"""
    bad_payload = booking_payload.copy()
    bad_payload.pop("phone")
    response = client.post("/api/bookings", json=bad_payload)
    assert response.status_code == 422

    bad_payload = booking_payload.copy()
    bad_payload["total_price"] = 0
    response = client.post("/api/bookings", json=bad_payload)
    assert response.status_code == 400
    assert "Итоговая сумма должна быть больше 0" in response.text


def test_calendar_event_missing_fields():
    """Проверка ошибок при отсутствии обязательных полей в календарном событии"""
    bad_payload = calendar_event_payload.copy()
    bad_payload.pop("phone")
    response = client.post("/api/calendar/events", json=bad_payload)
    assert response.status_code == 422

    bad_payload = calendar_event_payload.copy()
    bad_payload["total_price"] = 0
    response = client.post("/api/calendar/events", json=bad_payload)
    assert response.status_code == 400
    assert "Сумма должна быть больше 0" in response.text


def test_telegram_notify():
    """Проверка передачи всех данных для Telegram-уведомления"""
    notify_payload = {
        "name": "Тест Клиент",
        "phone": "79999999999",
        "date": "2025-05-22",
        "times": ["10:00", "11:00"],
        "total_price": 2500,  # исправлено
        "service": "Студийная фотосессия"
    }
    response = client.post("/api/telegram/notify", json=notify_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data
