from typing import Optional
import logging
from backend.app.core.config import settings
import aiohttp
import ssl
from backend.app.services.telegram_templates import booking_message_with_buttons

logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def send_booking_notification(self, message: str, booking_id: str = None, service=None, date=None, times=None, name=None, phone=None, total_price=None) -> bool:
        """
        Отправляет уведомление о бронировании в Telegram с inline-кнопками
        """
        try:
            if booking_id and service and date and times and name is not None and phone is not None and total_price is not None:
                text, buttons = booking_message_with_buttons(booking_id, service, date, times, name, phone, total_price)
                payload = {
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": {"inline_keyboard": buttons}
                }
            else:
                payload = {
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=payload) as resp:
                    if resp.status == 200:
                        logger.info(f"Sending Telegram notification: {payload['text']}")
                        return True
                    else:
                        logger.error(f"Telegram API error: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    async def send_booking_confirmation(
        self,
        booking_id: str,
        client_name: str,
        date: str,
        time: str,
        additional_info: Optional[str] = None
    ) -> bool:
        """
        Отправляет подтверждение бронирования в Telegram
        """
        try:
            message = (
                f"✅ Бронирование подтверждено\n\n"
                f"🆔 ID: {booking_id}\n"
                f"👤 Клиент: {client_name}\n"
                f"📅 Дата: {date}\n"
                f"🕒 Время: {time}\n"
            )
            
            if additional_info:
                message += f"\n📝 Дополнительная информация:\n{additional_info}"

            async with aiohttp.ClientSession() as session:
                payload = {
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
                async with session.post(self.api_url, data=payload) as resp:
                    if resp.status == 200:
                        logger.info(f"Sending booking confirmation: {message}")
                        return True
                    else:
                        logger.error(f"Telegram API error: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send booking confirmation: {e}")
            return False

    async def send_booking_cancellation(
        self,
        booking_id: str,
        client_name: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Отправляет уведомление об отмене бронирования в Telegram
        """
        try:
            message = (
                f"❌ Бронирование отменено\n\n"
                f"🆔 ID: {booking_id}\n"
                f"👤 Клиент: {client_name}\n"
            )
            
            if reason:
                message += f"\n📝 Причина отмены:\n{reason}"

            async with aiohttp.ClientSession() as session:
                payload = {
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
                async with session.post(self.api_url, data=payload) as resp:
                    if resp.status == 200:
                        logger.info(f"Sending cancellation notification: {message}")
                        return True
                    else:
                        logger.error(f"Telegram API error: {resp.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send cancellation notification: {e}")
            return False 