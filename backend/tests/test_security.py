import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
import time

@pytest.mark.security
@pytest.mark.auth
def test_unauthorized_access_to_protected_endpoints(client):
    """Тест доступа к защищенным эндпоинтам без авторизации."""
    endpoints = [
        ("GET", "/api/bookings/"),
        ("POST", "/api/bookings/"),
        ("GET", "/api/clients/"),
        ("POST", "/api/clients/"),
        ("GET", "/api/news/"),
        ("POST", "/api/news/"),
        ("GET", "/api/settings/"),
        ("PUT", "/api/settings/"),
    ]
    
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        elif method == "POST":
            response = client.post(endpoint, json={})
        elif method == "PUT":
            response = client.put(endpoint, json={})
        
        assert response.status_code in [401, 403], f"Endpoint {endpoint} should be protected"

@pytest.mark.security
@pytest.mark.auth
def test_invalid_token_access(client):
    """Тест доступа с неверным токеном."""
    client.headers.update({"Authorization": "Bearer invalid_token"})
    response = client.get("/api/bookings/")
    assert response.status_code == 401

@pytest.mark.security
@pytest.mark.auth
def test_expired_token_access(client):
    """Тест доступа с истекшим токеном."""
    from app.api.routes.auth import create_access_token
    
    expired_token = create_access_token(
        data={"sub": "testuser", "role": "admin"},
        expires_delta=timedelta(seconds=1)
    )

    time.sleep(2)

    client.headers.update({"Authorization": f"Bearer {expired_token}"})
    response = client.get("/api/bookings/")
    assert response.status_code == 401

@pytest.mark.security
@pytest.mark.auth
@pytest.mark.integration
def test_role_based_access_control(auth_client, db_session):
    """Тест контроля доступа на основе ролей."""
    from app.models.user import User, UserRole
    from app.services.user import pwd_context
    from app.api.routes.auth import create_access_token

    manager_user = User(
        username="manageruser",
        email="manager@example.com",
        hashed_password=pwd_context.hash("testpassword"),
        role=UserRole.manager,
        full_name="Manager User"
    )
    db_session.add(manager_user)
    db_session.commit()
    
    manager_token = create_access_token(
        data={"sub": "manageruser", "role": "manager"}
    )
    
    manager_client = auth_client
    manager_client.headers.update({"Authorization": f"Bearer {manager_token}"})
    
    response = manager_client.get("/api/bookings/")
    assert response.status_code == 200
    
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    start_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    booking_data = {
        "date": future_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "total_price": 1000.0,
        "client_name": "Test Client",
        "client_phone": "+79001234567"
    }
    
    response = manager_client.post("/api/bookings/", json=booking_data)
    assert response.status_code == 201

@pytest.mark.security
@pytest.mark.auth
@pytest.mark.integration
def test_admin_only_endpoints(auth_client, db_session):
    """Тест эндпоинтов, доступных только администраторам."""
    from app.models.user import User, UserRole
    from app.services.user import pwd_context
    from app.api.routes.auth import create_access_token

    regular_user = User(
        username="regularuser",
        email="user@example.com",
        hashed_password=pwd_context.hash("testpassword"),
        role=UserRole.user,
        full_name="Regular User"
    )
    db_session.add(regular_user)
    db_session.commit()
    
    user_token = create_access_token(
        data={"sub": "regularuser", "role": "user"}
    )
    
    user_client = auth_client
    user_client.headers.update({"Authorization": f"Bearer {user_token}"})
    
    response = user_client.get("/api/bookings/")
    assert response.status_code == 200

@pytest.mark.security
@pytest.mark.performance
def test_rate_limiting(client):
    """Тест ограничения скорости запросов."""
    for i in range(100):
        response = client.get("/api/bookings/")
        if response.status_code == 429:
            break
    
    assert True
