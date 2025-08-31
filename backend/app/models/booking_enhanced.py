from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, ForeignKey, Index, CheckConstraint, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .enhanced_base import EnhancedBase as Base
from .base_enhanced import EnhancedBase

class BookingState(str, enum.Enum):
    PENDING = "pending"      # Initial state, awaiting confirmation
    CONFIRMED = "confirmed"  # Confirmed and scheduled
    IN_PROGRESS = "in_progress"  # Currently happening
    COMPLETED = "completed"  # Finished successfully
    CANCELLED = "cancelled"  # Cancelled by client or admin
    NO_SHOW = "no_show"      # Client didn't show up

class BookingSource(str, enum.Enum):
    WEBSITE = "website"      # Booked through website
    PHONE = "phone"          # Booked via phone call
    WALK_IN = "walk_in"      # Walk-in booking
    ADMIN = "admin"          # Created by admin

class Booking(Base, EnhancedBase):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(20), unique=True, nullable=False)  # REF-YYYYMMDD-XXXX
    
    # Time management with timezone awareness
    booking_date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_hours = Column(Integer, nullable=False)  # Cached for performance
    
    # State management
    state = Column(String(20), default=BookingState.PENDING, nullable=False)
    state_history = Column(JSON, default=list)  # Track all state transitions
    
    # Client information (guest bookings)
    client_name = Column(String(200), nullable=False)
    client_phone = Column(String(20), nullable=False)
    client_phone_normalized = Column(String(15), nullable=False)  # E.164 format
    client_email = Column(String(255), nullable=True)
    
    # Booking details
    space_type = Column(String(50), nullable=False)
    equipment_requested = Column(JSON, default=dict)
    special_requirements = Column(Text, nullable=True)
    
    # Pricing
    base_price = Column(Numeric(10, 2), nullable=False)
    equipment_price = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_price = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String(20), default="pending")
    
    # Metadata
    source = Column(String(20), default=BookingSource.WEBSITE)
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)  # Staff-only notes
    
    # Relationships
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    employee = relationship("Employee", foreign_keys=[employee_id])
    
    calendar_event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=True)
    calendar_event = relationship("CalendarEvent", back_populates="bookings")
    
    # Performance optimization indexes
    __table_args__ = (
        Index("idx_booking_date_time", "booking_date", "start_time", "end_time"),
        Index("idx_booking_state", "state"),
        Index("idx_booking_phone", "client_phone_normalized"),
        Index("idx_booking_reference", "booking_reference"),
        Index("idx_booking_employee", "employee_id"),
        CheckConstraint("end_time > start_time", name="check_time_validity"),
        {'extend_existing': True}
        # Inherited from EnhancedBase: created_at, updated_at indexes
    )