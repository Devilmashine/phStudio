import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ..app.api.routes.gallery import router as gallery_router

# Минимальное приложение для теста
app = FastAPI()
app.include_router(gallery_router, prefix="/api/gallery")

client = TestClient(app)

def test_get_gallery_images_empty():
    # Этот тест не требует авторизации или базы данных
    response = client.get("/api/gallery/")
    assert response.status_code == 200
    assert response.json() == []
