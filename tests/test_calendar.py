import logging
logging.basicConfig(level=logging.INFO)
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.api.routes import calendar
from backend.app.utils import auth
from backend.app.models.user import UserSchema, UserRole
from backend.app.deps import get_current_user
import os

class FakeCalendarService:
    def get_available_slots(self, start_date, end_date):
        return [{"start": str(start_date), "end": str(end_date)}]
    def create_event(self, *a, **k):
        return {"id": "fake", "summary": "test"}
    def update_event(self, *a, **k):
        return {"id": "fake", "summary": "updated"}
    def delete_event(self, *a, **k):
        return True
    def get_event(self, *a, **k):
        return {"id": "fake", "summary": "test"}

@pytest.fixture(autouse=True)
def override_calendar_service():
    # Создаём файл логов для тестов по правильному пути
    log_dir = os.path.join(os.path.dirname(__file__), '../backend/app/logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'actions.log')
    with open(log_file, 'a', encoding='utf-8') as f:
        pass
    app.dependency_overrides[calendar.get_calendar_service] = lambda: FakeCalendarService()
    yield
    app.dependency_overrides = {}

client = TestClient(app)

def test_get_slots():
    response = client.get("/calendar/slots?start=2024-06-01T09:00:00&end=2024-06-01T21:00:00")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_export_bookings_admin():
    app.dependency_overrides[get_current_user] = lambda: UserSchema(username="admin", role=UserRole.admin)
    response = client.get("/calendar/bookings/export")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    app.dependency_overrides = {}

def test_export_logs_admin():
    app.dependency_overrides[get_current_user] = lambda: UserSchema(username="admin", role=UserRole.admin)
    response = client.get("/calendar/logs/export")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    app.dependency_overrides = {}

def test_export_logs_forbidden():
    app.dependency_overrides[get_current_user] = lambda: UserSchema(username="user", role=UserRole.user)
    response = client.get("/calendar/logs/export")
    assert response.status_code == 403
    app.dependency_overrides = {} 