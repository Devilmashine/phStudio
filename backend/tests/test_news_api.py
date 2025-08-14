import pytest
<<<<<<< HEAD
from fastapi import FastAPI
=======
>>>>>>> feature/employee-section
from fastapi.testclient import TestClient

<<<<<<< HEAD
@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(news_router, prefix="/api/news")

    def override_get_db():
        pass
    def override_get_current_active_user():
        pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    with TestClient(app) as c:
        yield c

def test_get_news_list(client):
=======
def test_get_news_list(client: TestClient):
    """
    Тест на получение пустого списка новостей.
    Использует фикстуру client, которая обеспечивает чистую БД.
    """
>>>>>>> feature/employee-section
    response = client.get("/api/news/")
    assert response.status_code == 200
    assert response.json() == []

# Тесты для создания/обновления/удаления новостей потребуют
# фикстуры для аутентифицированного пользователя (админа)
# и передачи токена в заголовках.
