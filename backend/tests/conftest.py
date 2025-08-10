import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..app.models.base import Base
from ..app.core.config import get_settings

@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    # Clear the cache to ensure test environment variables are loaded
    get_settings.cache_clear()
    """
    Устанавливает переменные окружения для всех тестов.
    Это гарантирует, что тесты не будут использовать продакшен базу данных.
    """
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["ENV"] = "testing"

import json
from ..app.models.settings import StudioSettings

@pytest.fixture(scope="function")
def db_session():
    """
    Фикстура для создания чистой базы данных для каждого теста.
    """
    # Import all models here to ensure they are registered with the Base
    from ..app import models
    engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

import pytest
from fastapi.testclient import TestClient
from ..app.core.database import get_db

@pytest.fixture(scope="function")
def client(db_session):
    """
    Фикстура для создания TestClient с переопределенной зависимостью БД.
    """
    from ..app.main import create_app
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # Disable rate limiter for tests
    from ..app.core.rate_limiter import default_rate_limit
    async def override_rate_limit():
        pass
    app.dependency_overrides[default_rate_limit] = override_rate_limit

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c


@pytest.fixture
def studio_settings(db_session):
    """Фикстура для создания настроек студии по умолчанию в тестовой БД."""
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
