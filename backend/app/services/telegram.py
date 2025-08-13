import requests
from typing import Optional
from app.core.config import settings


class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, text: str, parse_mode: Optional[str] = None) -> bool:
        """
        Отправляет сообщение в Telegram чат
        """
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
            }
            if parse_mode:
                data["parse_mode"] = parse_mode

            response = requests.post(url, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Ошибка при отправке сообщения в Telegram: {e}")
            return False

    async def send_booking_notification(self, booking_data: dict) -> bool:
        """
        Отправляет уведомление о новой брони
        """
        message = (
            "🎉 Новая бронь!\n\n"
            f"📅 Дата: {booking_data['date']}\n"
            f"⏰ Время: {booking_data['start_time']} - {booking_data['end_time']}\n"
            f"👤 Клиент: {booking_data['client_name']}\n"
            f"📞 Телефон: {booking_data['client_phone']}\n"
            f"💵 Сумма: {booking_data['total_price']} руб."
        )
        return await self.send_message(message)

    async def send_cancellation_notification(self, booking_data: dict) -> bool:
        """
        Отправляет уведомление об отмене брони
        """
        message = (
            "❌ Отмена брони!\n\n"
            f"📅 Дата: {booking_data['date']}\n"
            f"⏰ Время: {booking_data['start_time']} - {booking_data['end_time']}\n"
            f"👤 Клиент: {booking_data['client_name']}\n"
            f"📞 Телефон: {booking_data['client_phone']}"
        )
        return await self.send_message(message)


telegram_service = TelegramService()
