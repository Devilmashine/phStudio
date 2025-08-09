from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from backend.app.models.calendar_event import CalendarEvent
from backend.app.models.booking import Booking
from backend.app.schemas.calendar_event import CalendarEventCreate, CalendarEventResponse
from typing import List, Optional
import pytz

class CalendarService:
    def __init__(self, db: Session):
        self.db = db
        self.cache_ttl = timedelta(minutes=5)  # Время жизни кэша

    def _should_update_cache(self, event: CalendarEvent) -> bool:
        if not event.cache_updated_at:
            return True
        return datetime.now(pytz.UTC) - event.cache_updated_at > self.cache_ttl

    def _update_availability_cache(self, event: CalendarEvent):
        """Обновляет кэш доступности события"""
        # Проверяем связанные бронирования
        bookings = self.db.query(Booking).filter(
            Booking.calendar_event_id == event.id,
            Booking.status.in_(['confirmed', 'pending'])
        ).all()

        total_spots = event.people_count
        booked_spots = sum(booking.people_count for booking in bookings)
        
        if booked_spots >= total_spots:
            availability = 'fully_booked'
        elif booked_spots > 0:
            availability = 'partially_booked'
        else:
            availability = 'available'

        event.availability_cached = availability
        event.cache_updated_at = datetime.now(pytz.UTC)
        self.db.commit()

    def get_events(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[str] = None
    ) -> List[CalendarEvent]:
        """Получает события с оптимизированным запросом и кэшированием"""
        query = self.db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.start_time >= start_date,
                CalendarEvent.end_time <= end_date
            )
        )

        if status:
            query = query.filter(CalendarEvent.status == status)

        events = query.all()

        # Обновляем кэш для событий, где это необходимо
        for event in events:
            if self._should_update_cache(event):
                self._update_availability_cache(event)

        return events
