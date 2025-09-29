from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone, time
from app.core.database import get_db
from app.models.booking import BookingLegacy
from app.models.booking import BookingStatus
from app.utils.timezone import get_moscow_date_range, to_moscow_time, MOSCOW_TZ
from pydantic import BaseModel

# Response models for new bulk endpoints
class MonthAvailabilitySlots(BaseModel):
    available_slots: int
    total_slots: int
    booked_slots: int

class TimeSlot(BaseModel):
    time: str
    available: bool

class DayDetailsResponse(BaseModel):
    date: str
    slots: List[TimeSlot]

router = APIRouter()

@router.get("/month-availability", response_model=Dict[str, MonthAvailabilitySlots])
async def get_month_availability(
    year: int = Query(..., description="Year (e.g., 2025)"),
    month: int = Query(..., description="Month (1-12)"),
    db: Session = Depends(get_db)
):
    """
    PUBLIC ENDPOINT: Get bulk availability data for an entire month.
    Returns: {"2025-08-26": {"available_slots": 8, "total_slots": 12, "booked_slots": 4}}
    """
    try:
        # Calculate month date range in Moscow timezone and convert to UTC
        moscow_start = MOSCOW_TZ.localize(datetime(year, month, 1, 0, 0, 0))
        if month == 12:
            moscow_end = MOSCOW_TZ.localize(datetime(year + 1, 1, 1, 0, 0, 0)) - timedelta(seconds=1)
        else:
            moscow_end = MOSCOW_TZ.localize(datetime(year, month + 1, 1, 0, 0, 0)) - timedelta(seconds=1)

        month_start_utc = moscow_start.astimezone(timezone.utc)
        month_end_utc = moscow_end.astimezone(timezone.utc)

        print(f"Fetching month availability (UTC): {month_start_utc} to {month_end_utc}")

        total_slots_per_day = 12
        booked_hours_by_date: Dict[str, set[int]] = {}

        # Fetch bookings overlapping the month window
        bookings = db.query(BookingLegacy).filter(
            BookingLegacy.start_time < month_end_utc,
            BookingLegacy.end_time > month_start_utc
        ).all()

        print(f"Found {len(bookings)} bookings in month {year}-{month}")

        def status_value(status) -> str:
            if isinstance(status, BookingStatus):
                return status.value
            return str(status).lower() if status else ""

        for booking in bookings:
            if status_value(getattr(booking, "status", None)) in {"cancelled", "completed"}:
                continue

            start_local = to_moscow_time(booking.start_time)
            end_local = to_moscow_time(booking.end_time)

            if end_local <= start_local:
                end_local = start_local + timedelta(hours=1)

            current = start_local.replace(minute=0, second=0, microsecond=0)

            while current < end_local:
                if 9 <= current.hour <= 20:
                    date_str = current.strftime('%Y-%m-%d')
                    booked_hours = booked_hours_by_date.setdefault(date_str, set())
                    booked_hours.add(current.hour)

                current += timedelta(hours=1)

        result = {}
        current_date = moscow_start.date()
        end_date_only = moscow_end.date()

        today_moscow = to_moscow_time(datetime.now(timezone.utc)).date()

        while current_date <= end_date_only:
            if current_date >= today_moscow:
                date_str = current_date.strftime('%Y-%m-%d')
                booked_slots = len(booked_hours_by_date.get(date_str, set()))
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
    PUBLIC ENDPOINT: Get detailed slot information for a specific day.
    Returns: {"date": "2025-08-26", "slots": [{"time": "10:00", "available": true}]}
    """
    try:
        print(f"Fetching day details for: {date}")

        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        window_start_utc, window_end_utc = get_moscow_date_range(date)

        bookings = db.query(BookingLegacy).filter(
            BookingLegacy.start_time < window_end_utc,
            BookingLegacy.end_time > window_start_utc
        ).all()

        print(f"Found {len(bookings)} bookings for {date} (UTC range: {window_start_utc} to {window_end_utc})")

        booked_hours = set()

        def status_value(status) -> str:
            if isinstance(status, BookingStatus):
                return status.value
            return str(status).lower() if status else ""

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

        for booking in bookings:
            if status_value(getattr(booking, "status", None)) in {"cancelled", "completed"}:
                continue
            mark_interval(booking.start_time, booking.end_time)

        slots = []
        for hour in range(9, 21):
            time_str = f"{hour:02d}:00"
            slots.append({
                "time": time_str,
                "available": hour not in booked_hours
            })

        result = {
            "date": date,
            "slots": slots
        }

        print(f"Returning {len(slots)} slots for {date}, booked hours: {sorted(booked_hours)}")
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        print(f"Error in get_day_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")