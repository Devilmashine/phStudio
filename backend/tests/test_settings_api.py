import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_token(username, password):
    resp = client.post("/api/token", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]

def create_test_user(username, password, role):
    # Создаём пользователя через /api/users (требует админа, поэтому сначала создаём супер-админа напрямую)
    from backend.app.services.user import UserService
    from backend.app.models.user import UserRole
    from backend.app.core.database import get_db
    db = next(get_db())
    user_service = UserService(db)
    if not user_service.get_user_by_username(username):
        user_service.create_user(type("UserCreate", (), {"username": username, "email": f"{username}@test.com", "password": password, "role": role, "full_name": username})())

def test_settings_crud_flow():
    admin_username = "test_admin"
    admin_password = "test_admin_pass"
    manager_username = "test_manager"
    manager_password = "test_manager_pass"

    # Создать тестовых пользователей
    create_test_user(admin_username, admin_password, "admin")
    create_test_user(manager_username, manager_password, "manager")

    # Получить токены
    admin_token = get_token(admin_username, admin_password)
    manager_token = get_token(manager_username, manager_password)

    # Без токена — 401
    response = client.get("/api/settings/")
    assert response.status_code == 401

    # CRUD как админ
    payload = {
        "name": "Test Studio",
        "description": "Test description",
        "contacts": "test@example.com",
        "prices": "1000-2000",
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
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/api/settings/", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["base_price_per_hour"] == 2500.0
    assert data["work_days"] == ["mon", "tue", "wed", "thu", "fri"]

    # Обновление настроек как админ
    update_payload = payload.copy()
    update_payload["base_price_per_hour"] = 3000.0
    response = client.put("/api/settings/", json=update_payload, headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["base_price_per_hour"] == 3000.0

    # Получение настроек как админ
    response = client.get("/api/settings/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["base_price_per_hour"] == 3000.0

    # Получение настроек как менеджер
    headers_manager = {"Authorization": f"Bearer {manager_token}"}
    response = client.get("/api/settings/", headers=headers_manager)
    assert response.status_code == 200
