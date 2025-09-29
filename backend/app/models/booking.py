from sqlalchemy import Column, Integer, String, DateTime, Float, Enum as SAEnum, Index, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from .base import Base

class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

    @classmethod
    def from_db_value(cls, value):
        """Convert database value to enum"""
        if value is None:
            return None
        return cls(value)

    def to_db_value(self):
        """Convert enum to database value"""
        return self.value

class BookingLegacy(Base):
    __tablename__ = "bookings_legacy"
    __table_args__ = (
        Index("idx_bookings_date_range", "start_time", "end_time"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    # Use SQLAlchemy Enum for PostgreSQL compatibility
    status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    total_price = Column(Float, nullable=False)

    # Клиент - увеличиваем размеры полей для PostgreSQL
    client_name = Column(String(200), nullable=False)
    client_phone = Column(String(20), nullable=False)
    client_email = Column(String(255), nullable=True)
    phone_normalized = Column(String(20), nullable=True)  # Для оптимизации поиска

    # Дополнительная информация
    notes = Column(Text, nullable=True)  # Use Text for longer notes
    people_count = Column(Integer, nullable=False, default=1)
    
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Связи
    calendar_event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=True)
    calendar_event = relationship("CalendarEvent", back_populates="bookings", foreign_keys=[calendar_event_id])
