from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.booking import Booking
from app.utils.timezone import get_moscow_date_range, to_moscow_time
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
        # Calculate month date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        print(f"Fetching month availability: {start_date} to {end_date}")
        
        # Working hours: 9:00-20:00 = 12 total slots per day
        total_slots_per_day = 12
        
        # Get all bookings for the month
        bookings = db.query(Booking).filter(
            Booking.start_time >= start_date,
            Booking.start_time <= end_date
        ).all()
        
        print(f"Found {len(bookings)} bookings in month {year}-{month}")
        
        # Count booked slots per day
        booked_slots_by_date = {}
        
        for booking in bookings:
            booking_date = booking.start_time.date()
            date_str = booking_date.strftime('%Y-%m-%d')
            
            # Calculate duration in hours (minimum 1 hour)
            duration_hours = max(1, int((booking.end_time - booking.start_time).total_seconds() / 3600))
            
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
    PUBLIC ENDPOINT: Get detailed slot information for a specific day.
    Returns: {"date": "2025-08-26", "slots": [{"time": "10:00", "available": true}]}
    """
    try:
        print(f"Fetching day details for: {date}")
        
        # Get UTC date range for the Moscow date
        utc_start, utc_end = get_moscow_date_range(date)
        
        # Query bookings using UTC range
        bookings = db.query(Booking).filter(
            Booking.start_time >= utc_start,
            Booking.start_time <= utc_end
        ).all()
        
        print(f"Found {len(bookings)} bookings for {date} (UTC range: {utc_start} to {utc_end})")
        
        # Track booked hours in Moscow time
        booked_hours = set()
        
        for booking in bookings:
            # Convert to Moscow time for hour calculation
            # booking.start_time and booking.end_time are already datetime objects
            moscow_start = to_moscow_time(booking.start_time)
            moscow_end = to_moscow_time(booking.end_time)
            
            print(f"Booking: Moscow {moscow_start} to {moscow_end}")
            
            start_hour = moscow_start.hour
            end_hour = moscow_end.hour
            
            # If booking ends with minutes (e.g., 09:30), include that hour
            if moscow_end.minute > 0:
                end_hour += 1
            
            # Mark all hours that are affected by the booking
            for hour in range(start_hour, end_hour):
                if 9 <= hour <= 20:  # Only working hours
                    booked_hours.add(hour)
                    print(f"Marking hour {hour}:00 as booked")
        
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
        
        print(f"Returning {len(slots)} slots for {date}, booked hours: {sorted(booked_hours)}")
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        print(f"Error in get_day_details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")