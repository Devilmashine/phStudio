import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_settings_crud_flow():
    # 1. Попытка получить настройки (ожидаем 404)
    response = client.get("/api/settings/")
    assert response.status_code == 404

    # 2. Создание настроек
    payload = {
        "work_days": ["mon", "tue", "wed", "thu", "fri"],
        "work_start_time": "09:00",
        "work_end_time": "20:00",
        "base_price_per_hour": 2500.0,
        "weekend_price_multiplier": 1.5,
        "telegram_notifications_enabled": True,
        "email_notifications_enabled": True,
        "holidays": ["2025-01-01", "2025-05-09"],
        "min_booking_duration": 1,
        "max_booking_duration": 8,
        "advance_booking_days": 30
    }
    response = client.post("/api/settings/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["base_price_per_hour"] == 2500.0
    assert data["work_days"] == ["mon", "tue", "wed", "thu", "fri"]

    # 3. Обновление настроек
    update_payload = payload.copy()
    update_payload["base_price_per_hour"] = 3000.0
    response = client.put("/api/settings/", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["base_price_per_hour"] == 3000.0

    # 4. Получение настроек (должны быть обновлены)
    response = client.get("/api/settings/")
    assert response.status_code == 200
    data = response.json()
    assert data["base_price_per_hour"] == 3000.0
