from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any
from backend.app.core.database import get_db
from backend.app.services.google_calendar import GoogleCalendarService
from backend.app.services.log_service import export_logs
import backend.app.utils.auth as auth
from fastapi.responses import StreamingResponse
from io import StringIO
import csv
from backend.app.models.user import UserSchema, UserRole
from backend.app.deps import get_current_user

router = APIRouter()

def get_calendar_service():
    return GoogleCalendarService()

@router.get("/availability/{target_date}", response_model=List[Dict[str, Any]])
async def get_availability(
    target_date: date,
    db: Session = Depends(get_db),
    calendar_service: GoogleCalendarService = Depends(get_calendar_service)
):
    """Получение доступных временных слотов на указанную дату"""
    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)
    slots = calendar_service.get_available_slots(start_dt, end_dt)
    return slots

@router.get("/calendar/slots")
def get_slots(start: str, end: str, calendar_service: GoogleCalendarService = Depends(get_calendar_service)):
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    return calendar_service.get_available_slots(start_dt, end_dt)

@router.get("/calendar/bookings/export")
def export_bookings(calendar_service: GoogleCalendarService = Depends(get_calendar_service)):
    now = datetime.now(timezone.utc)
    events = calendar_service.get_available_slots(now - timedelta(days=30), now + timedelta(days=1))
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["start", "end"])
    writer.writeheader()
    for e in events:
        writer.writerow(e)
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=bookings.csv"})

@router.get("/calendar/logs/export")
def export_logs_api(user: UserSchema = Depends(get_current_user)):
    print(f"DEBUG export_logs_api: user={user}")
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    logs = export_logs()
    return StreamingResponse(StringIO(logs), media_type="text/plain", headers={"Content-Disposition": "attachment; filename=logs.txt"})

@router.get("/events", response_model=List[Dict[str, Any]])
async def get_events(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    calendar_service: GoogleCalendarService = Depends(get_calendar_service)
):
    """Получение событий календаря за период"""
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.min.time()) + timedelta(days=1)
    # Получаем все события через Google Calendar API
    events = calendar_service.service.events().list(
        calendarId=calendar_service.calendar_id,
        timeMin=start_dt.isoformat() + 'Z',
        timeMax=end_dt.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    return events