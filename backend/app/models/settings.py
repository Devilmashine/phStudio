from sqlalchemy import Column, Integer, String
from .base import Base


class StudioSettings(Base):
    __tablename__ = "studio_settings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    contacts = Column(String(255), nullable=True)
    prices = Column(String(255), nullable=True)
    work_days = Column(String(1024), nullable=False, default="[]")  # JSON-строка
    work_start_time = Column(String(5), nullable=False, default="09:00")
    work_end_time = Column(String(5), nullable=False, default="20:00")
    base_price_per_hour = Column(String(32), nullable=False, default="1000")
    weekend_price_multiplier = Column(String(8), nullable=False, default="1.5")
    telegram_notifications_enabled = Column(String(8), nullable=False, default="1")
    email_notifications_enabled = Column(String(8), nullable=False, default="1")
    holidays = Column(String(1024), nullable=True)  # JSON-строка
    min_booking_duration = Column(String(8), nullable=False, default="1")
    max_booking_duration = Column(String(8), nullable=False, default="8")
    advance_booking_days = Column(String(8), nullable=False, default="30")
