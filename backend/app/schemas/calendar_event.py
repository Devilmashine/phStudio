from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    people_count: int

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventUpdate(CalendarEventBase):
    pass

class CalendarEventResponse(CalendarEventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
