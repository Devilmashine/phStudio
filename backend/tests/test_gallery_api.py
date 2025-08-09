import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ..app.api.routes.gallery import router as gallery_router

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(gallery_router, prefix="/api/gallery")
    with TestClient(app) as c:
        yield c

def test_get_gallery_images_empty(client):
    # Этот тест не требует авторизации или базы данных
    response = client.get("/api/gallery/")
    assert response.status_code == 200
    assert response.json() == []
