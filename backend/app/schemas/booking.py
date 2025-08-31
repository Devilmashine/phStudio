from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from ..models.booking import BookingStatus
from ..utils.timezone import parse_moscow_datetime


class BookingBase(BaseModel):
    date: datetime
    start_time: datetime
    end_time: datetime
    total_price: float
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    notes: Optional[str] = None
    people_count: int


class BookingCreate(BookingBase):
    @field_validator('date', 'start_time', 'end_time', mode='before')
    @classmethod
    def parse_moscow_times(cls, v):
        """Parse datetime strings as Moscow time"""
        if isinstance(v, str):
            return parse_moscow_datetime(v)
        return v


class Booking(BookingBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    calendar_event_id: Optional[str] = None

    class ConfigDict:
        from_attributes = True


class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class MessageResponse(BaseModel):
    message: str