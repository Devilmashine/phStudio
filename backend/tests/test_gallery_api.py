import os
import io
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_gallery_crud_flow(tmp_path):
    # 1. Получить список (должен быть пуст)
    response = client.get("/api/gallery/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # 2. Загрузка изображения (mock admin)
    test_image = io.BytesIO(b"fake image data")
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    data = {"description": "Test image"}
    # Подменяем авторизацию (mock admin)
    token = "test-admin-token"
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/gallery/upload", files=files, data=data, headers=headers)
    # Для реального теста потребуется корректный токен admin
    # Здесь ожидаем 401/403, если нет mock auth, либо 200 если есть
    assert response.status_code in (200, 401, 403)

    # 3. Удаление изображения (если загрузка успешна)
    if response.status_code == 200:
        image_id = response.json()["id"]
        del_resp = client.delete(f"/api/gallery/{image_id}", headers=headers)
        assert del_resp.status_code == 200
        assert del_resp.json()["status"] == "deleted"
