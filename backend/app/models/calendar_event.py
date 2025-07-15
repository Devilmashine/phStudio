from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.models.base import Base
from backend.app.models.calendar_event_status import CalendarEventStatus

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    people_count = Column(Integer, nullable=False)
    status = Column(SAEnum(CalendarEventStatus), nullable=False, default=CalendarEventStatus.pending)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    # Можно добавить внешние ключи на booking_id, user_id при необходимости
