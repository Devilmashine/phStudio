from typing import Optional
import logging
from app.core.config import get_settings
import aiohttp
import ssl
from app.services.telegram_templates import booking_message_with_buttons

logger = logging.getLogger(__name__)


class TelegramBotService:
    def __init__(self):
        settings = get_settings()
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def send_booking_notification(
        self,
        message: str,
        booking_id: str = None,
        service=None,
        date=None,
        times=None,
        name=None,
        phone=None,
        total_price=None,
        people_count=None,
    ) -> bool:
        """
        Отправляет уведомление о бронировании в Telegram с inline-кнопками
        """
        # Явная строгая валидация всех параметров
        if not service or not isinstance(service, str) or not service.strip():
            raise ValueError("Параметр 'service' обязателен и должен быть строкой")
        if not date or not isinstance(date, str) or not date.strip():
            raise ValueError("Параметр 'date' обязателен и должен быть строкой")
        if (
            not times
            or not isinstance(times, (list, tuple))
            or not all(isinstance(t, str) and t.strip() for t in times)
        ):
            raise ValueError(
                "Параметр 'times' обязателен и должен быть списком строк и не пустым"
            )
        if not name or not isinstance(name, str) or not name.strip():
            raise ValueError("Имя клиента обязательно и должно быть строкой")
        if not phone or not isinstance(phone, str) or not phone.strip():
            raise ValueError("Телефон клиента обязателен и должен быть строкой")
        try:
            price_val = int(total_price)
            if price_val <= 0:
                raise ValueError("Цена должна быть больше 0")
        except Exception as e:
            raise ValueError(f"Некорректная цена: {total_price}, ошибка: {e}")
        if (
            people_count is None
            or not isinstance(people_count, int)
            or people_count < 1
        ):
            raise ValueError(
                "Количество человек обязательно и должно быть положительным целым числом"
            )

        logger.info(
            f"Параметры для отправки уведомления: service={service}, date={date}, times={times}, name={name}, phone={phone}, total_price={total_price}, people_count={people_count}"
        )
        text, buttons = booking_message_with_buttons(
            service, date, times, name, phone, total_price, people_count
        )
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": {"inline_keyboard": buttons},
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload) as resp:
                    if resp.status == 200:
                        logger.info(f"Sending Telegram notification: {payload['text']}")
                        return True
                    else:
                        logger.error(
                            f"Telegram API error: {resp.status}, Response: {await resp.text()}"
                        )
                        logger.info(f"Ответ Telegram API: {await resp.text()}")
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
        additional_info: Optional[str] = None,
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
                    "parse_mode": "HTML",
                }
                async with session.post(self.api_url, json=payload) as resp:
                    if resp.status == 200:
                        logger.info(f"Sending booking confirmation: {message}")
                        return True
                    else:
                        logger.error(
                            f"Telegram API error: {resp.status}, Response: {await resp.text()}"
                        )
                        return False
        except Exception as e:
            logger.error(f"Failed to send booking confirmation: {e}")
            return False

    async def send_booking_cancellation(
        self, booking_id: str, client_name: str, reason: Optional[str] = None
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
                    "parse_mode": "HTML",
                }
                async with session.post(self.api_url, json=payload) as resp:
                    if resp.status == 200:
                        logger.info(f"Sending cancellation notification: {message}")
                        return True
                    else:
                        logger.error(
                            f"Telegram API error: {resp.status}, Response: {await resp.text()}"
                        )
                        return False
        except Exception as e:
            logger.error(f"Failed to send cancellation notification: {e}")
            return False
