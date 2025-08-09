from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SAEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base
from .calendar_event_status import CalendarEventStatus

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    __table_args__ = (
        Index('idx_calendar_events_date_range', 'start_time', 'end_time'),
        Index('idx_calendar_events_status', 'status')
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    people_count = Column(Integer, nullable=False)
    status = Column(SAEnum(CalendarEventStatus), nullable=False, default=CalendarEventStatus.pending)
    
    # Оптимизация через кэширование
    availability_cached = Column(String(20), nullable=True)
    cache_updated_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Связи
    bookings = relationship("Booking", back_populates="calendar_event")
