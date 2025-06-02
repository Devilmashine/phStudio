from backend.app.services.google_calendar import GoogleCalendarService
from backend.app.services.telegram_bot import TelegramBotService
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from backend.app.models.booking import Booking as BookingModel
from backend.app.schemas.booking import BookingCreate
from typing import List, Optional

logger = logging.getLogger(__name__)

class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def get_booking(self, booking_id: int) -> Optional[BookingModel]:
        return self.db.query(BookingModel).filter(BookingModel.id == booking_id).first()

    def get_bookings(self, skip: int = 0, limit: int = 100) -> List[BookingModel]:
        return self.db.query(BookingModel).offset(skip).limit(limit).all()

    def create_booking(self, booking_data: BookingCreate) -> BookingModel:
        booking = BookingModel(**booking_data.dict())
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def delete_booking(self, booking_id: int) -> bool:
        booking = self.get_booking(booking_id)
        if not booking:
            return False
        self.db.delete(booking)
        self.db.commit()
        return True

    def update_booking(self, booking_id: int, booking_data) -> Optional[BookingModel]:
        booking = self.get_booking(booking_id)
        if not booking:
            return None
        for field, value in booking_data.dict(exclude_unset=True).items():
            setattr(booking, field, value)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    @staticmethod
    def legacy_create_booking(data):
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
