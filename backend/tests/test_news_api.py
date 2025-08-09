import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from ..app.api.routes.news import router as news_router
from ..app.deps import get_current_active_user, get_db

# Создаем минимальное приложение только для этого теста
app = FastAPI()
app.include_router(news_router, prefix="/api/news")

# Мокаем зависимости
def override_get_db():
    # Эта зависимость будет переопределена в тестах, где нужна сессия
    pass

def override_get_current_active_user():
    # Эта зависимость будет переопределена в тестах
    pass

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_active_user] = override_get_current_active_user

client = TestClient(app)

# --- Тесты ---
def test_get_news_list():
    # Этот тест не требует базы данных или авторизации
    response = client.get("/api/news/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
