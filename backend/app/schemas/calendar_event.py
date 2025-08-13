from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.models.calendar_event_status import CalendarEventStatus


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    people_count: int
    status: Optional[CalendarEventStatus] = CalendarEventStatus.pending


class CalendarEventCreate(CalendarEventBase):
    pass

from typing import Any
class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    people_count: Optional[int] = None
    status: Optional[CalendarEventStatus] = None


class CalendarEventResponse(CalendarEventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
