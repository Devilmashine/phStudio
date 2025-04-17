import pytest
from backend.app.services.telegram_bot import TelegramBotService
import asyncio
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_send_booking_notification(monkeypatch):
    service = TelegramBotService()
    # Корректный мок aiohttp
    class FakeResp:
        status = 200
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
    class FakeSession:
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass
        def post(self, *a, **k):
            return FakeResp()
    monkeypatch.setattr("aiohttp.ClientSession", lambda: FakeSession())
    result = await service.send_booking_notification("Test message")
    assert result is True

def test_telegram_webhook():
    data = {"message": {"chat": {"id": 123}, "text": "/start"}}
    response = client.post("/telegram/webhook", json=data)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 