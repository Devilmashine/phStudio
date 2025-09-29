from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone, time
from app.core.database import get_db
from app.services.calendar_event import CalendarEventService
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse, MessageResponse, IcalTokenResponse
from app.models.user import User, UserRole
from app.deps import get_current_admin, get_current_manager
from fastapi.responses import Response, StreamingResponse
from ics import Calendar, Event as IcsEvent
from secrets import token_urlsafe
from app.models.calendar_event import CalendarEvent
from app.models.booking import BookingLegacy
from app.utils.timezone import to_moscow_time, get_moscow_date_range
from pydantic import BaseModel
from sqlalchemy import func, text

router = APIRouter(
    tags=["calendar-events"],
    # Отключаем автоматический редирект при отсутствии завершающего слеша
    redirect_slashes=False,
)

# Response models for new bulk endpoints
class MonthAvailabilitySlots(BaseModel):
    available_slots: int
    total_slots: int
    booked_slots: int

class MonthAvailabilityResponse(BaseModel):
    data: Dict[str, MonthAvailabilitySlots]

class TimeSlot(BaseModel):
    time: str
    available: bool

class DayDetailsResponse(BaseModel):
    date: str
    slots: List[TimeSlot]


@router.get("/", response_model=List[CalendarEventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format"),
    event_status: str = None,
    db: Session = Depends(get_db),
):
    try:
        from datetime import timedelta

        # Convert string dates to datetime objects
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_dt = (
            datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            if end_date
            else None
        )

        service = CalendarEventService(db)
        events = service.get_events(
            skip=skip,
            limit=limit,
            start_date=start_dt,
            end_date=end_dt,
            status=event_status,
        )
        return events
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат даты: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager),
):
    service = CalendarEventService(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event


@router.post("/", response_model=CalendarEventResponse)
async def create_event(
    event_data: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = CalendarEventService(db)
    return service.create_event(event_data)


@router.put("/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = CalendarEventService(db)
    event = service.update_event(event_id, event_data)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event


@router.delete("/{event_id}", response_model=MessageResponse)
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = CalendarEventService(db)
    ok = service.delete_event(event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return {"message": "Событие удалено"}


@router.get("/ical/{user_id}/{token}", response_class=Response)
async def get_ical_for_user(user_id: int, token: str, db: Session = Depends(get_db)):
    # Проверка токена пользователя (реализовать хранение токена в User)
    user = db.query(User).filter(User.id == user_id).first()
    if not user or getattr(user, "ical_token", None) != token:
        raise HTTPException(status_code=403, detail="Недействительный токен")
    events = db.query(CalendarEvent).all()
    cal = Calendar()
    for e in events:
        ics_event = IcsEvent()
        ics_event.name = e.title
        ics_event.begin = e.start_time
        ics_event.end = e.end_time
        ics_event.description = e.description or ""
        cal.events.add(ics_event)
    return Response(content=str(cal), media_type="text/calendar")


@router.get("/{event_id}/ical", response_class=Response)
async def get_ical_for_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    cal = Calendar()
    ics_event = IcsEvent()
    ics_event.name = event.title
    ics_event.begin = event.start_time
    ics_event.end = event.end_time
    ics_event.description = event.description or ""
    cal.events.add(ics_event)
    return Response(content=str(cal), media_type="text/calendar")


@router.post("/ical-token/reset/{user_id}", response_model=IcalTokenResponse)
async def reset_ical_token(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.ical_token = token_urlsafe(32)
    db.commit()
    db.refresh(user)
    return {"ical_token": user.ical_token}


# NEW BULK AVAILABILITY ENDPOINTS

@router.get("/month-availability", response_model=Dict[str, MonthAvailabilitySlots])
async def get_month_availability(
    year: int = Query(..., description="Year (e.g., 2025)"),
    month: int = Query(..., description="Month (1-12)"),
    db: Session = Depends(get_db)
):
    """
    Get bulk availability data for an entire month.
    Returns: {"2025-08-26": {"available_slots": 8, "total_slots": 12, "booked_slots": 4}}
    """
    try:
        # Calculate month date range (use timezone-aware datetimes - UTC)
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end_date = (datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1))
        else:
            end_date = (datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1))
        
        print(f"Fetching month availability: {start_date} to {end_date}")
        
        # Working hours: 9:00-20:00 = 12 total slots per day
        total_slots_per_day = 12
        
        # Get all calendar events for the month with better query optimization
        events_query = db.query(CalendarEvent).filter(
            CalendarEvent.start_time >= start_date,
            CalendarEvent.start_time <= end_date
        )
        
        # Use execution options for better performance
        events = events_query.all()
        
        print(f"Found {len(events)} events in month {year}-{month}")
        
        # Count booked slots per day more efficiently
        booked_slots_by_date = {}
        
        for event in events:
            event_date = event.start_time.date()
            date_str = event_date.strftime('%Y-%m-%d')
            
            # Calculate duration in hours (minimum 1 hour)
            duration_hours = max(1, int((event.end_time - event.start_time).total_seconds() / 3600))
            
            if date_str not in booked_slots_by_date:
                booked_slots_by_date[date_str] = 0
            
            booked_slots_by_date[date_str] += duration_hours
        
        # Generate response for all days in month
        result = {}
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            # Skip past dates
            if current_date >= datetime.now().date():
                date_str = current_date.strftime('%Y-%m-%d')
                booked_slots = min(booked_slots_by_date.get(date_str, 0), total_slots_per_day)
                available_slots = max(0, total_slots_per_day - booked_slots)
                
                result[date_str] = {
                    "available_slots": available_slots,
                    "total_slots": total_slots_per_day,
                    "booked_slots": booked_slots
                }
            
            current_date += timedelta(days=1)
        
        print(f"Returning availability for {len(result)} days")
        return result
        
    except Exception as e:
        print(f"Error in get_month_availability: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/day-details", response_model=DayDetailsResponse)
async def get_day_details(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Get detailed slot information for a specific day.
    Returns: {"date": "2025-08-26", "slots": [{"time": "10:00", "available": true}]}
    """
    try:
        # Parse date
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        print(f"Fetching day details for: {target_date}")
        
        # Skip past dates
        if target_date < datetime.now().date():
            raise HTTPException(status_code=400, detail="Cannot get details for past dates")
        
        # Get events for this specific day with optimized query
        window_start_utc, window_end_utc = get_moscow_date_range(date)

        events_query = db.query(CalendarEvent).filter(
            CalendarEvent.start_time < window_end_utc,
            CalendarEvent.end_time > window_start_utc
        )
        
        events = events_query.all()
        
        print(f"Found {len(events)} events for {date}")
        
        # Track booked hours more efficiently (from calendar events and bookings)
        booked_hours = set()

        def mark_interval(start_dt, end_dt):
            if start_dt is None or end_dt is None:
                return
            start_local = to_moscow_time(start_dt)
            end_local = to_moscow_time(end_dt)
            if end_local <= start_local:
                end_local = start_local + timedelta(hours=1)

            for hour in range(9, 21):
                slot_start_local = to_moscow_time(
                    datetime.combine(target_date, time(hour))
                )
                slot_end_local = slot_start_local + timedelta(hours=1)
                if slot_start_local < end_local and slot_end_local > start_local:
                    booked_hours.add(hour)

        # Mark hours from calendar events
        for event in events:
            mark_interval(event.start_time, event.end_time)

        # Also include bookings (bookings_legacy) so frontend sees booked slots
        try:
            print(f"\n=== Processing bookings for {target_date} ===")
            print(f"Search window (UTC): {window_start_utc} to {window_end_utc}")
            bookings = db.query(BookingLegacy).filter(
                BookingLegacy.start_time < window_end_utc,
                BookingLegacy.end_time > window_start_utc
            ).all()
            print(f"Found {len(bookings)} bookings overlapping window")
            for idx, b in enumerate(bookings, 1):
                print(f"\nBooking #{idx}:")
                print(f"  ID: {b.id}")
                print(f"  Raw start_time: {b.start_time} ({type(b.start_time).__name__})")
                print(f"  Raw end_time: {b.end_time} ({type(b.end_time).__name__})")
                print(f"  Status: {b.status}")
            for b in bookings:
                # Skip obviously cancelled or completed bookings (if status exists)
                status = getattr(b, 'status', None)
                if status and str(status).lower() in ('cancelled', 'completed'):
                    print(f"  Skipping booking {b.id} due to status {status}")
                    continue
                mark_interval(b.start_time, b.end_time)
        except Exception:
            # If bookings table doesn't exist or query fails, ignore and continue with events only
            pass
        
        # Generate slots for 9:00-20:00
        slots = []
        for hour in range(9, 21):  # 9:00 to 20:00
            time_str = f"{hour:02d}:00"
            available = hour not in booked_hours
            
            slots.append({
                "time": time_str,
                "available": available
            })
        
        result = {
            "date": date,
            "slots": slots
        }
        
        print(f"Returning {len(slots)} slots for {date}")
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        print(f"Error in get_day_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
