import pytest
import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from alembic.config import Config
from alembic import command
from fastapi.testclient import TestClient

# Add the project root to the path to allow imports from the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.base import Base
from app.core.config import get_settings
from app.models.studio_settings import StudioSettings
from app.models.news import News
from app.core.database import get_db

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    """Sets environment variables for the entire test session."""
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["ENV"] = "testing"
    get_settings.cache_clear()

@pytest.fixture(scope="session")
def engine():
    """Creates a test database engine that persists for the entire session."""
    return create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

@pytest.fixture(scope="session")
def migrated_db_connection(engine):
    """
    Creates a single connection for the entire test session and applies migrations.
    """
    connection = engine.connect()
    try:
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
        # Pass the connection to alembic
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
        yield connection
    finally:
        connection.close()

@pytest.fixture(scope="function")
def db_session(migrated_db_connection):
    """
    Creates a new database session for each test function, using nested transactions.
    This ensures that each test runs in isolation.
    """
    transaction = migrated_db_connection.begin_nested()
    Session = sessionmaker(bind=migrated_db_connection)
    session = Session()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Creates a TestClient with the database dependency overridden.
    """
    from app.main import app, include_routers

    # Ensure all routers are included in the app for testing
    include_routers(app)

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    # Disable rate limiter for tests
    from app.core.rate_limiter import default_rate_limit
    async def override_rate_limit():
        pass
    app.dependency_overrides[default_rate_limit] = override_rate_limit

    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def auth_client(client, test_user):
    """
    Creates an authenticated TestClient.
    """
    from app.api.routes.auth import create_access_token
    
    access_token = create_access_token(
        data={"sub": test_user.username, "role": test_user.role.name}
    )
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client

@pytest.fixture
def studio_settings(db_session):
    """Fixture to create default studio settings in the test DB."""
    settings_data = {
        "name": "Test Studio", "contacts": "test", "prices": "100",
        "work_days": json.dumps(['mon', 'tue', 'wed', 'thu', 'fri']),
        "holidays": json.dumps(["2025-01-01"]),
        "work_start_time": "10:00", "work_end_time": "20:00",
        "base_price_per_hour": "1000", "weekend_price_multiplier": "1.5",
        "telegram_notifications_enabled": "1", "email_notifications_enabled": "1",
        "min_booking_duration": "1", "max_booking_duration": "8", "advance_booking_days": "30"
    }
    settings = StudioSettings(**settings_data)
    db_session.add(settings)
    db_session.commit()
    return settings

@pytest.fixture
def test_user(db_session):
    """Fixture to create a test user."""
    from app.models.user import User, UserRole
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": pwd_context.hash("testpassword"),
        "role": UserRole.admin,
        "full_name": "Test User"
    }
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_news(db_session, test_user):
    """Fixture to create a test news item."""
    news_data = {
        "title": "Test News",
        "content": "Test content",
        "author_id": test_user.id,
        "published": 1
    }
    news = News(**news_data)
    db_session.add(news)
    db_session.commit()
    db_session.refresh(news)
    return news
