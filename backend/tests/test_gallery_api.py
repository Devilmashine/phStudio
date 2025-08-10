import pytest
from fastapi.testclient import TestClient

def test_get_gallery_images_empty(client: TestClient):
    """
    Тест на получение пустого списка изображений из галереи.
    Использует фикстуру client, которая обеспечивает чистую БД.
    """
    response = client.get("/api/gallery/")
    assert response.status_code == 200
    assert response.json() == []

# Можно добавить тесты для добавления/удаления изображений,
# но для этого потребуется реализовать загрузку файлов в тестах
# и, возможно, мокать систему хранения файлов.
