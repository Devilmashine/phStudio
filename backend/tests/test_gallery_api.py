import pytest
from fastapi.testclient import TestClient

<<<<<<< HEAD
@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(gallery_router, prefix="/api/gallery")
    with TestClient(app) as c:
        yield c

def test_get_gallery_images_empty(client):
    # Этот тест не требует авторизации или базы данных
=======
def test_get_gallery_images_empty(client: TestClient):
    """
    Тест на получение пустого списка изображений из галереи.
    Использует фикстуру client, которая обеспечивает чистую БД.
    """
>>>>>>> feature/employee-section
    response = client.get("/api/gallery/")
    assert response.status_code == 200
    assert response.json() == []

# Можно добавить тесты для добавления/удаления изображений,
# но для этого потребуется реализовать загрузку файлов в тестах
# и, возможно, мокать систему хранения файлов.
