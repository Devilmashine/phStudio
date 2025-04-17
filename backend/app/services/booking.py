from backend.app.services.google_calendar import GoogleCalendarService
from backend.app.services.telegram_bot import TelegramBotService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BookingService:
    @staticmethod
    def create_booking(data):
        try:
            calendar_service = GoogleCalendarService()
            telegram_service = TelegramBotService()

            booking_result = calendar_service.create_event(
                start_time=datetime.fromisoformat(f"{data['date']}T{data['time']}"),
                description=data.get('description', '')
            )
            
            # Формируем текст уведомления
            message = f"🎥 Новое бронирование:\n\n" \
                      f"📅 Дата: {data['date']}\n" \
                      f"🕒 Время: {data['time']}\n"
            
            # Добавляем комментарий, если есть
            if data.get('description') and data['description'].strip():
                message += f"\n💬 Комментарий: {data['description']}"

            # Отправка уведомления в телеграм
            telegram_service.send_booking_notification(message)
            
            return {
                'status': 'success',
                'message': 'Бронирование создано',
                'booking_details': booking_result
            }
        
        except Exception as e:
            logger.error(f"Booking error: {e}")
            return {
                'status': 'error',
                'message': 'Ошибка бронирования'
            }
