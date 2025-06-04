import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.app.main import app
from fastapi.testclient import TestClient
import pytest
from backend.app.models.base import Base
from backend.app.core.database import engine

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Создать все таблицы для тестовой БД
    Base.metadata.create_all(bind=engine)
    yield
    # Можно добавить очистку, если нужно

# --- Авторизация ---
def admin_headers():
    return {
        "X-User-Role": "admin",
        "X-User-Id": "1",
        "X-User-Name": "admin"
    }

def manager_headers():
    return {
        "X-User-Role": "manager",
        "X-User-Id": "2",
        "X-User-Name": "manager"
    }

def test_create_news_unauthorized():
    response = client.post("/api/news/", json={
        "title": "Тестовая новость",
        "content": "Текст новости",
        "published": 1
    })
    assert response.status_code == 401

# --- ADMIN ---
def test_create_news_admin():
    response = client.post("/api/news/", json={
        "title": "Новость от админа",
        "content": "Контент",
        "published": 1
    }, headers=admin_headers())
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Новость от админа"
    global created_news_id
    created_news_id = data["id"]

def test_update_news_admin():
    response = client.put(f"/api/news/{created_news_id}", json={
        "title": "Новость обновлена",
        "content": "Обновленный контент",
        "published": 1
    }, headers=admin_headers())
    assert response.status_code == 200
    assert response.json()["title"] == "Новость обновлена"

def test_delete_news_admin():
    response = client.delete(f"/api/news/{created_news_id}", headers=admin_headers())
    assert response.status_code == 204

def test_get_deleted_news():
    response = client.get(f"/api/news/{created_news_id}")
    assert response.status_code == 404

# --- MANAGER ---
def test_create_news_manager_forbidden():
    response = client.post("/api/news/", json={
        "title": "Новость от менеджера",
        "content": "Контент",
        "published": 1
    }, headers=manager_headers())
    assert response.status_code == 403

def test_update_news_manager_forbidden():
    response = client.put(f"/api/news/{created_news_id}", json={
        "title": "Попытка менеджера",
        "content": "fail",
        "published": 1
    }, headers=manager_headers())
    assert response.status_code == 403 or response.status_code == 404

def test_delete_news_manager_forbidden():
    response = client.delete(f"/api/news/{created_news_id}", headers=manager_headers())
    assert response.status_code == 403 or response.status_code == 404

# --- LIST & NOT FOUND ---
def test_get_news_list():
    response = client.get("/api/news/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_news_not_found():
    response = client.get("/api/news/999999")
    assert response.status_code == 404
