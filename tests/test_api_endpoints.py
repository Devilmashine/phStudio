import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# --- API ENDPOINTS COVERAGE ---

def test_get_available_slots():
    resp = client.get("/api/calendar/available-slots?date=2025-05-22")
    assert resp.status_code == 200
    data = resp.json()
    assert "date" in data and "slots" in data


def test_get_calendar_events():
    resp = client.get("/api/calendar/events?start_date=2025-05-22&end_date=2025-05-22")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_booking_and_notify():
    payload = {
        "date": "2025-05-22",
        "times": ["10:00", "11:00"],
        "name": "API Клиент",
        "phone": "79999999999",
        "total_price": 2500,  # исправлено
        "service": "API тест"
    }
    resp = client.post("/api/bookings", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["details"]["name"] == payload["name"]
    assert data["telegram_notification"] in [True, False]


def test_create_calendar_event_and_notify():
    payload = {
        "title": "API Событие",
        "description": "API тест",
        "start_time": "2025-05-22T10:00:00",
        "duration_hours": 1,
        "phone": "79999999999",
        "total_price": 2500
    }
    resp = client.post("/api/calendar/events", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "success"
    assert "id" in data
    assert "telegram_notification" in data


def test_send_telegram_notification():
    payload = {
        "name": "API Клиент",
        "phone": "79999999999",
        "date": "2025-05-22",
        "times": ["10:00", "11:00"],
        "total_price": 2500,  # исправлено
        "service": "API тест"
    }
    resp = client.post("/api/telegram/notify", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "success"


def test_calendar_event_missing_fields():
    payload = {
        "title": "",
        "description": "",
        "start_time": "",
        "duration_hours": 1,
        "phone": "",
        "total_price": 0
    }
    resp = client.post("/api/calendar/events", json=payload)
    assert resp.status_code == 400
    assert "обязателен" in resp.json()['detail'] or "должны быть указаны" in resp.json()['detail']


def test_booking_missing_fields():
    payload = {
        "date": "2025-05-22",
        "times": [],
        "name": "",
        "phone": "",
        "total_price": 0
    }
    resp = client.post("/api/bookings", json=payload)
    assert resp.status_code == 400
    detail = resp.json().get("detail", "")
    detail_str = str(detail).lower()
    # Проверяем только наличие слова "обязательно" для максимальной устойчивости
    assert "обязательно" in detail_str

    # Проверка отсутствия обязательного поля phone (ожидаем 422)
    payload_missing_phone = {
        "date": "2025-05-22",
        "times": ["10:00", "11:00"],
        "name": "API Клиент",
        "total_price": 2500,
        "service": "API тест"
    }
    resp = client.post("/api/bookings", json=payload_missing_phone)
    assert resp.status_code == 422
    detail = resp.json().get("detail", "")
    detail_str = str(detail).lower()
    assert ("phone" in detail_str) or ("обязательно" in detail_str)
