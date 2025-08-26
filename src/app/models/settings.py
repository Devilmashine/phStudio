from datetime import time
from sqlalchemy import Column, Integer, String, Time, Float, Boolean, JSON
from app.models.base import Base

class StudioSettings(Base):
    __tablename__ = "studio_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Рабочие часы
    work_days = Column(JSON, nullable=False)  # Список рабочих дней недели
    work_start_time = Column(Time, nullable=False)
    work_end_time = Column(Time, nullable=False)
    
    # Цены
    base_price_per_hour = Column(Float, nullable=False)
    weekend_price_multiplier = Column(Float, default=1.5)
    
    # Настройки уведомлений
    telegram_notifications_enabled = Column(Boolean, default=True)
    email_notifications_enabled = Column(Boolean, default=True)
    
    # Праздничные дни
    holidays = Column(JSON, nullable=True)  # Список дат в формате YYYY-MM-DD
    
    # Дополнительные настройки
    min_booking_duration = Column(Integer, default=1)  # Минимальная длительность бронирования в часах
    max_booking_duration = Column(Integer, default=8)  # Максимальная длительность бронирования в часах
    advance_booking_days = Column(Integer, default=30)  # За сколько дней можно бронировать 