from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta, timezone
from app.services.google_calendar import GoogleCalendarService
from app.utils.auth import get_current_user, require_role
from app.services.log_service import log_action, export_logs
from app.models.user import UserRole
from fastapi.responses import StreamingResponse
from io import StringIO
import csv

def get_calendar_service():
    return GoogleCalendarService()

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/slots")
def get_slots(start: str, end: str, user=Depends(get_current_user), calendar_service: GoogleCalendarService = Depends(get_calendar_service)):
    log_action(user.username, "get_slots", f"{start} - {end}")
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    return calendar_service.get_available_slots(start_dt, end_dt)

@router.post("/event", dependencies=[Depends(require_role(UserRole.user))])
def create_event(data: dict, user=Depends(get_current_user), calendar_service: GoogleCalendarService = Depends(get_calendar_service)):
    event = calendar_service.create_event(
        summary=data["summary"],
        start_time=datetime.fromisoformat(data["start_time"]),
        end_time=datetime.fromisoformat(data["end_time"]),
        description=data.get("description"),
        attendees=data.get("attendees")
    )
    log_action(user.username, "create_event", f"{event.get('id')}")
    return event

@router.put("/event/{event_id}", dependencies=[Depends(require_role(UserRole.user))])
def update_event(event_id: str, data: dict, user=Depends(get_current_user), calendar_service: GoogleCalendarService = Depends(get_calendar_service)):
    event = calendar_service.update_event(event_id, **data)
    log_action(user.username, "update_event", event_id)
    return event

@router.delete("/event/{event_id}", dependencies=[Depends(require_role(UserRole.admin))])
def delete_event(event_id: str, user=Depends(get_current_user), calendar_service: GoogleCalendarService = Depends(get_calendar_service)):
    result = calendar_service.delete_event(event_id)
    log_action(user.username, "delete_event", event_id)
    return {"deleted": result}

@router.get("/event/{event_id}")
def get_event(event_id: str, user=Depends(get_current_user), calendar_service: GoogleCalendarService = Depends(get_calendar_service)):
    log_action(user.username, "get_event", event_id)
    return calendar_service.get_event(event_id)

@router.get("/logs/export", dependencies=[Depends(require_role(UserRole.admin))])
def export_logs_api():
    logs = export_logs()
    return StreamingResponse(StringIO(logs), media_type="text/plain", headers={"Content-Disposition": "attachment; filename=logs.txt"})

@router.get("/bookings/export", dependencies=[Depends(require_role(UserRole.admin))])
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