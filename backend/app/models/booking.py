from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone

from .base import Base


class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        Index("idx_bookings_date_range", "start_time", "end_time"),
        Index("idx_bookings_status", "status"),
        Index("idx_bookings_phone", "phone_normalized"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default=BookingStatus.PENDING.value, nullable=False)
    total_price = Column(Float, nullable=False)

    # Клиент
    client_name = Column(String, nullable=False)
    client_phone = Column(String, nullable=False)
    client_email = Column(String, nullable=True)
    phone_normalized = Column(String(20), nullable=True)  # Для оптимизации поиска

    # Дополнительная информация
    notes = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Связи
    calendar_event_id = Column(Integer, ForeignKey("calendar_events.id"))
    calendar_event = relationship("CalendarEvent", back_populates="bookings")
