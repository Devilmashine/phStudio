from sqlalchemy.orm import Session
from ..models.calendar_event import CalendarEvent
from ..schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate
from typing import List, Optional
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

class CalendarEventService:
    def __init__(self, db: Session):
        self.db = db

    def get_event(self, event_id: int) -> Optional[CalendarEvent]:
        return self.db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()

    def get_events(
        self,
        skip: int = 0,
        limit: int = 100,
        start_date: datetime = None,
        end_date: datetime = None,
        status: str = None
    ) -> List[CalendarEvent]:
        try:
            logger.info(f"Fetching events with params: start_date={start_date}, end_date={end_date}, status={status}")
            query = self.db.query(CalendarEvent)
            
            if start_date:
                query = query.filter(CalendarEvent.start_time >= start_date)
            if end_date:
                query = query.filter(CalendarEvent.end_time <= end_date)
            if status:
                query = query.filter(CalendarEvent.status == status)
                
            events = query.offset(skip).limit(limit).all()
            logger.info(f"Found {len(events)} events")
            return events
        except Exception as e:
            logger.error(f"Error fetching events: {str(e)}")
            raise
            
        return query.offset(skip).limit(limit).all()

    def create_event(self, event_data: CalendarEventCreate) -> CalendarEvent:
        event = CalendarEvent(**event_data.model_dump())
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_event(self, event_id: int, event_data: CalendarEventUpdate) -> Optional[CalendarEvent]:
        event = self.get_event(event_id)
        if not event:
            return None
        for field, value in event_data.model_dump(exclude_unset=True).items():
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
