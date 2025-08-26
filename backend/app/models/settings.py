from sqlalchemy import Column, Integer, String, Boolean, Numeric, JSON, Text
from .base import Base


class StudioSettings(Base):
    __tablename__ = "studio_settings"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # Use Text for longer descriptions
    contacts = Column(Text, nullable=True)  # Use Text for contact information
    prices = Column(Text, nullable=True)  # Use Text for price information
    
    # Use JSON column for PostgreSQL native JSON support
    work_days = Column(JSON, nullable=False, default=list)  # JSON array
    holidays = Column(JSON, nullable=True, default=list)  # JSON array
    
    # Time fields with proper validation
    work_start_time = Column(String(5), nullable=False, default="09:00")
    work_end_time = Column(String(5), nullable=False, default="20:00")
    
    # Use Numeric for precise monetary calculations
    base_price_per_hour = Column(Numeric(10, 2), nullable=False, default=1000.00)
    weekend_price_multiplier = Column(Numeric(4, 2), nullable=False, default=1.50)
    
    # Use Boolean for notifications settings
    telegram_notifications_enabled = Column(Boolean, nullable=False, default=True)
    email_notifications_enabled = Column(Boolean, nullable=False, default=True)
    
    # Use Integer for duration and days settings
    min_booking_duration = Column(Integer, nullable=False, default=1)  # hours
    max_booking_duration = Column(Integer, nullable=False, default=8)  # hours
    advance_booking_days = Column(Integer, nullable=False, default=30)  # days
    
    # Additional settings for photo studio
    timezone = Column(String(50), nullable=False, default="UTC")
    currency = Column(String(3), nullable=False, default="RUB")
    booking_confirmation_required = Column(Boolean, nullable=False, default=True)
