import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.services.telegram_bot import TelegramBotService
from aioresponses import aioresponses

class TestTelegramBotService(unittest.IsolatedAsyncioTestCase):
    async def test_send_booking_notification_with_valid_data(self):
        service = "Студийная фотосессия"
        date = "2025-05-12"
        times = ["10:00", "12:00"]
        name = "Иван Иванов"
        phone = "+79991234567"
        total_price = 5000

        with aioresponses() as m:
            bot_service = TelegramBotService()
            m.post(bot_service.api_url, status=200)

            result = await bot_service.send_booking_notification(
                message="Test Message",
                booking_id="123",
                service=service,
                date=date,
                times=times,
                name=name,
                phone=phone,
                total_price=total_price
            )

            self.assertTrue(result)

    async def test_send_booking_notification_with_missing_data(self):
        bot_service = TelegramBotService()

        with self.assertRaises(ValueError) as context:
            await bot_service.send_booking_notification(
                message="Test Message",
                booking_id=None,
                service=None,
                date=None,
                times=None,
                name=None,
                phone=None,
                total_price=None
            )

        self.assertEqual(str(context.exception), "Параметр 'service' обязателен и должен быть строкой")

if __name__ == "__main__":
    unittest.main()
