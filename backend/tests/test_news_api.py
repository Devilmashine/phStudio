import pytest
from fastapi.testclient import TestClient

def test_get_news_list(client: TestClient):
    """
    Тест на получение пустого списка новостей.
    Использует фикстуру client, которая обеспечивает чистую БД.
    """
    response = client.get("/api/news/")
    assert response.status_code == 200
    assert response.json() == []

# Тесты для создания/обновления/удаления новостей потребуют
# фикстуры для аутентифицированного пользователя (админа)
# и передачи токена в заголовках.
