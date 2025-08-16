import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes.settings import router as settings_router

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(settings_router, prefix="/api/settings")
    with TestClient(app) as c:
        yield c

def test_get_settings_unauthorized(client):
    response = client.get("/api/settings/")
    assert response.status_code == 401
