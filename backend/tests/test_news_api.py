import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ..app.api.routes.news import router as news_router
from ..app.deps import get_current_active_user, get_db

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
    response = client.get("/api/news/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
