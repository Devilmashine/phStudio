from sqlalchemy.orm import Session
from backend.app.models.calendar_event import CalendarEvent
from backend.app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate
from typing import List, Optional

class CalendarEventService:
    def __init__(self, db: Session):
        self.db = db

    def get_event(self, event_id: int) -> Optional[CalendarEvent]:
        return self.db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()

    def get_events(self, skip: int = 0, limit: int = 100, status: str = None) -> List[CalendarEvent]:
        query = self.db.query(CalendarEvent)
        if status:
            query = query.filter(CalendarEvent.status == status)
        return query.offset(skip).limit(limit).all()

    def create_event(self, event_data: CalendarEventCreate) -> CalendarEvent:
        event = CalendarEvent(**event_data.dict())
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_event(self, event_id: int, event_data: CalendarEventUpdate) -> Optional[CalendarEvent]:
        event = self.get_event(event_id)
        if not event:
            return None
        for field, value in event_data.dict(exclude_unset=True).items():
            setattr(event, field, value)
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, event_id: int) -> bool:
        event = self.get_event(event_id)
        if not event:
            return False
        self.db.delete(event)
        self.db.commit()
        return True
