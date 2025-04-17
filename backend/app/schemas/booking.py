from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookingBase(BaseModel):
    date: datetime
    start_time: datetime
    end_time: datetime
    total_price: float
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    notes: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    calendar_event_id: Optional[str] = None

    class Config:
        from_attributes = True 