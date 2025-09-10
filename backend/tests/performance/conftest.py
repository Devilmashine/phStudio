"""
Configuration for performance tests
"""

import pytest
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, get_engine
from app.core.config import get_settings

# Test configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def test_session_local(test_engine):
    """Create test database session factory"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    yield SessionLocal

@pytest.fixture(scope="function")
def db_session(test_session_local):
    """Create database session for testing"""
    session = test_session_local()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Create test client"""
    def override_get_db():
        try:
            db = test_session_local()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def auth_client(client: TestClient) -> TestClient:
    """Create authenticated test client"""
    # In a real implementation, this would authenticate the client
    # For now, we'll just return the regular client
    return client

# Performance test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "stress: mark test as stress test")
    config.addinivalue_line("markers", "benchmark: mark test as benchmark test")

# Skip performance tests by default
def pytest_collection_modifyitems(config, items):
    """Skip performance tests by default"""
    if config.getoption("--performance"):
        # Run performance tests
        return
    
    # Skip performance tests
    skip_performance = pytest.mark.skip(reason="need --performance option to run")
    for item in items:
        if "performance" in item.keywords:
            item.add_marker(skip_performance)

def pytest_addoption(parser):
    """Add command line options"""
    parser.addoption(
        "--performance",
        action="store_true",
        default=False,
        help="Run performance tests"
    )
    parser.addoption(
        "--stress",
        action="store_true",
        default=False,
        help="Run stress tests"
    )
    parser.addoption(
        "--benchmark",
        action="store_true",
        default=False,
        help="Run benchmark tests"
    )