import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ..app.api.routes.settings import router as settings_router

# Минимальное приложение для теста
app = FastAPI()
app.include_router(settings_router, prefix="/api/settings")

client = TestClient(app)

def test_get_settings_unauthorized():
    # Этот тест не требует авторизации или базы данных
    response = client.get("/api/settings/")
    assert response.status_code == 401
