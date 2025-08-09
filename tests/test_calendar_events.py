import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app
from backend.app.models.user import UserRole
from backend.app.deps import get_current_user
from backend.app.models.calendar_event import CalendarEvent
from backend.app.schemas.calendar_event import CalendarEventCreate
from sqlalchemy.orm import Session
from backend.app.core.database import get_db

# Test client
client = TestClient(app)

# Mock user for authentication
mock_user = {
    "id": 1,
    "email": "test@example.com",
    "role": UserRole.admin,
    "is_active": True
}

def get_test_user():
    return mock_user

app.dependency_overrides[get_current_user] = get_test_user

@pytest.fixture
def db_session(mocker):
    # Create a mock session
    session = mocker.MagicMock(spec=Session)
    
    # Override the get_db dependency
    app.dependency_overrides[get_db] = lambda: session
    
    return session

def test_create_calendar_event(db_session):
    event_data = {
        "title": "Test Event",
        "description": "Test Description",
        "start_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "duration_hours": 2,
        "status": "pending",
        "people_count": 2
    }
    
    # Mock the add and commit methods
    db_session.add.return_value = None
    db_session.commit.return_value = None
    
    # Mock the refreshed event
    mock_event = CalendarEvent(id=1, **event_data)
    db_session.refresh.return_value = None
    
    response = client.post("/api/calendar-events/", json=event_data)
    
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["title"] == event_data["title"]
    assert response.json()["people_count"] == event_data["people_count"]

def test_get_calendar_events(db_session):
    # Mock the query results
    mock_events = [
        CalendarEvent(
            id=1,
            title="Test Event 1",
            description="Description 1",
            start_time=datetime.now(),
            duration_hours=2,
            status="pending",
            people_count=2
        ),
        CalendarEvent(
            id=2,
            title="Test Event 2",
            description="Description 2",
            start_time=datetime.now() + timedelta(days=1),
            duration_hours=1,
            status="confirmed",
            people_count=3
        )
    ]
    
    db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_events
    
    response = client.get("/api/calendar-events/")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Test Event 1"
    assert response.json()[1]["title"] == "Test Event 2"

def test_update_calendar_event(db_session):
    event_id = 1
    update_data = {
        "title": "Updated Event",
        "description": "Updated Description",
        "people_count": 4
    }
    
    # Mock the query result
    mock_event = CalendarEvent(
        id=event_id,
        title="Original Event",
        description="Original Description",
        start_time=datetime.now(),
        duration_hours=2,
        status="pending",
        people_count=2
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_event
    
    response = client.patch(f"/api/calendar-events/{event_id}", json=update_data)
    
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]
    assert response.json()["people_count"] == update_data["people_count"]

def test_delete_calendar_event(db_session):
    event_id = 1
    
    # Mock the query result
    mock_event = CalendarEvent(
        id=event_id,
        title="Test Event",
        description="Test Description",
        start_time=datetime.now(),
        duration_hours=2,
        status="pending",
        people_count=2
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_event
    
    response = client.delete(f"/api/calendar-events/{event_id}")
    
    assert response.status_code == 200
    assert db_session.delete.called_once_with(mock_event)
    assert db_session.commit.called_once()
