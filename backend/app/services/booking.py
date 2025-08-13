from app.services.telegram_bot import TelegramBotService
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from app.models.booking import Booking as BookingModel
from app.schemas.booking import BookingCreate
from typing import List, Optional

logger = logging.getLogger(__name__)


class BookingService:
    def __init__(self, db: Session):
        self.db = db
<<<<<<< HEAD
=======
        self.settings_service = StudioSettingsService(db)

    def _validate_booking(self, booking_data: BookingCreate):
        """Проверяет, возможно ли создание бронирования."""
        # 1. Проверка на бронирование в прошлом
        if booking_data.start_time < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя бронировать на прошедшее время.",
            )

        # 2. Проверка на пересечение с существующими бронированиями
        overlapping_booking = (
            self.db.query(BookingModel)
            .filter(
                and_(
                    booking_data.start_time < BookingModel.end_time,
                    booking_data.end_time > BookingModel.start_time,
                )
            )
            .filter(
                BookingModel.status.in_(
                    [BookingStatus.CONFIRMED, BookingStatus.PENDING]
                )
            )
            .first()
        )

        if overlapping_booking:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Выбранное время уже занято.",
            )

        # 3. Проверка на соответствие рабочим часам и дням
        import json

        settings = self.settings_service.get_settings()
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Настройки студии не найдены.",
            )

        # Десериализация JSON полей из настроек
        try:
            work_days = json.loads(settings.work_days)
            holidays = json.loads(settings.holidays) if settings.holidays else []
        except (json.JSONDecodeError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка конфигурации рабочих дней студии.",
            )

        booking_date_str = booking_data.start_time.strftime("%Y-%m-%d")
        if booking_date_str in holidays:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Студия не работает в праздничные дни.",
            )

        booking_day_of_week = booking_data.start_time.strftime("%a").lower()
        if booking_day_of_week not in work_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Студия не работает в этот день недели.",
            )

        work_start_time = datetime.strptime(settings.work_start_time, "%H:%M").time()
        work_end_time = datetime.strptime(settings.work_end_time, "%H:%M").time()

        if not (
            work_start_time <= booking_data.start_time.time()
            and booking_data.end_time.time() <= work_end_time
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Бронирование выходит за рамки рабочего времени студии.",
            )
>>>>>>> origin/backend-audit-and-fixes

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

<<<<<<< HEAD
    def update_booking(self, booking_id: int, booking_data) -> Optional[BookingModel]:
=======
    def update_booking(
        self, booking_id: int, booking_data: BookingCreate
    ) -> Optional[BookingModel]:
>>>>>>> origin/backend-audit-and-fixes
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
            telegram_service = TelegramBotService()
            
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
